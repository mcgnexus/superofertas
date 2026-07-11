export interface Producto {
  id?: string;
  nombre: string;
  precio: number;
  precio_original?: number;
  descuento?: number;
  supermercado: string;
  categoria: string;
  imagen?: string;
  ubicacion?: string;
  fecha?: string;
  descripcion?: string;
}

export interface Oferta extends Producto {}

export interface DiaMenu {
  desayuno?: Producto;
  comida?: Producto;
  cena?: Producto;
}

export interface MenuSemanal {
  id?: string;
  dias: { [key: string]: DiaMenu };
  total_coste: number;
  presupuesto_utilizado: number;
  supermercados_usados: string[];
  precio_promedio_comida: number;
}

export interface OfertaFilters {
  supermercado?: string;
  categoria?: string;
  precio_max?: number;
}