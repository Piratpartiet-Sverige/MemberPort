import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration
from app.database.dao.users import UsersDao
from app.web.handlers.base import BaseHandler
from app.config import Config
from tornado import httpclient
from app.logger import logger


class SignInHandler(BaseHandler):
    def get(self):
        request = self.get_argument("request", default="")

        if (request == ""):
            return self.redirect("http://127.0.0.1:8888/.ory/kratos/public/self-service/browser/flows/login")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""
        error = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                # Get the request context of browser-based registration user flows
                api_response = api_instance.get_self_service_browser_login_request(request)
                csrf_token = api_response.methods['password'].config.fields[-1].value
                if api_response.methods['password'].config.errors != None:
                    error = api_response.methods['password'].config.errors[0].message
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_browser_login_request: %s\n" % e)

        logger.debug("csrf_token: " + csrf_token)

        self.render("sign-in.html", request=request, csrf_token=csrf_token, error=error)


class SignUpHandler(BaseHandler):
    def get(self):
        request = self.get_argument("request", default="")

        if (request == ""):
            return self.redirect("http://127.0.0.1:8888/.ory/kratos/public/self-service/browser/flows/registration")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""
        error = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.AdminApi(api_client)
            try:
                api_response = api_instance.get_self_service_browser_registration_request(request)
                csrf_token = api_response.methods['password'].config.fields[0].value
                inputs = api_response.methods['password'].config.fields
                if api_response.methods['password'].config.errors != None:
                    error = api_response.methods['password'].config.errors[0].message
            except ApiException as e:
                logger.error("Exception when calling AdminApi->get_self_service_browser_registration_request: %s\n" % e)
            except ValueError as e:
                logger.error("Exception when calling PublicApi->get_self_service_browser_registration_request: %s\n" % e)

        logger.debug("csrf_token: " + csrf_token)

        self.render("sign-up.html", request=request, csrf_token=csrf_token, error=error, inputs=inputs)

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

