export class OrgData {
  id: string
  name: string
  description: string
  active: boolean
  path: string

  constructor (id: string, name: string, description: string, active: boolean, path: string) {
    this.id = id
    this.name = name
    this.description = description
    this.active = active
    this.path = path
  }
}
