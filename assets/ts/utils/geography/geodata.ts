export class GeoData {
  id: string
  name: string
  type: GEO_TYPES
  path: string | undefined
  area: string | undefined
  active: boolean | undefined

  constructor (id: string, name: string, type: GEO_TYPES, path: string | undefined, area: string | undefined) {
    this.id = id
    this.name = name
    this.type = type
    this.path = path
    this.area = area
  }
}

export enum GEO_TYPES {
  COUNTRY = 'COUNTRY',
  AREA = 'AREA',
  MUNICIPALITY = 'MUNICIPALITY',
}

export function getNodeType (id: string, geodata: { [id: string]: GeoData }): GEO_TYPES {
  if (geodata[id].path !== undefined) {
    return GEO_TYPES.AREA
  } else if (geodata[id].area !== undefined) {
    return GEO_TYPES.MUNICIPALITY
  } else {
    return GEO_TYPES.COUNTRY
  }
}
