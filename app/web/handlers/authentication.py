from app.database.dao.users import UsersDao
from app.web.handlers.base import BaseHandler
from app.config import Config


class SignInHandler(BaseHandler):
    def get(self):
        self.render("sign-in.html", error="")

    async def post(self):
        email = self.get_argument("email")
        password = self.get_argument("password")

        if email is None or password is None:
            self.render("sign-in.html", error="E-mail och/eller lösenord var tomt")
            return

        dao = UsersDao(self.db)
        result = await dao.check_user_password(email, password)
        if result.valid:
            ip = self.request.remote_ip
            session = await dao.new_session(result.user.id, ip)
            self.set_session_cookie(session.hash)
            self.redirect("/")
        else:
            self.render("sign-in.html", error="E-mail och/eller lösenord var felaktigt")


class SignUpHandler(BaseHandler):
    def get(self):
        self.render("sign-up.html", error="")

    async def post(self):
        email = self.get_argument("email")
        name = self.get_argument("name")
        password = self.get_argument("password")
        password2 = self.get_argument("password2")

        if email is None:
            self.render("sign-up.html", error="E-mail saknas")
            return
        elif name is None:
            self.render("sign-up.html", error="Namn saknas")
            return
        elif password is None or password2 is None:
            self.render("sign-up.html", error="Lösenord saknas")
            return
        elif password != password2:
            self.render("sign-up.html", error="Lösenorden matchar inte varandra")
            return

        config = Config.get_config()
        max_email_length = config.getint("Users", "max_email_length")
        max_name_length = config.getint("Users", "max_username_length")
        max_password_length = config.getint("Users", "max_password_length")
        min_password_length = config.getint("Users", "min_password_length")

        if len(email) > max_email_length:
            max = max_email_length.__str__()
            self.render("sign-up.html", error="E-mail adressen får inte vara längre än " + max + " tecken")
            return
        elif len(name) > max_name_length:
            max = max_name_length.__str__()
            self.render("sign-up.html", error="Namnet får inte vara längre än " + max + " tecken")
            return
        elif len(password) > max_password_length:
            max = max_password_length.__str__()
            self.render("sign-up.html", error="Lösenordet får inte vara längre än " + max + " tecken")
            return
        elif len(password) < min_password_length:
            min = min_password_length.__str__()
            self.render("sign-up.html", error="Lösenordet måste minst vara " + min + " tecken långt")
            return

        dao = UsersDao(self.db)
        user = await dao.create_user(name, email, password)

        if user is None:
            self.render("sign-up.html", error="E-mail: " + email + " är redan registrerad")

        session = await dao.new_session(user.id, self.request.remote_ip)

        self.set_session_cookie(session.hash)
        self.redirect("/")


class SignOutHandler(BaseHandler):
    async def get(self):
        dao = UsersDao(self.db)
        if self.session_hash is not None:
            await dao.remove_session(self.session_hash)
            self.clear_session_cookie()
        self.redirect("/")

