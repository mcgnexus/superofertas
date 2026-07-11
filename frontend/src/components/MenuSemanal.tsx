import { useState } from 'react';
import type { DiaMenu, MenuSemanal } from '../types';

function MenuSemanal({ menu }: { menu: MenuSemanal }) {
  const diasSemana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

  const getComidaTipo = (comida: any) => {
    if (!comida) return null;
    return (
      <div className="bg-gray-50 rounded-lg p-3">
        <h4 className="font-medium text-gray-800 mb-1 text-sm">{comida.nombre}</h4>
        <p className="text-xs text-gray-600">€{comida.precio.toFixed(2)}</p>
        <p className="text-xs text-gray-500 mt-1 line-clamp-2">{comida.descripcion || 'Sin descripción'}</p>
      </div>
    );
  };

  const getDiaComidas = () => {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {Object.entries(menu.dias).map(([dia, comidas]) => (
          <div key={dia} className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="font-bold text-lg mb-3 text-verde">
              {diasSemana[parseInt(dia)] || `Día ${dia}`}
            </h3>
            <div className="space-y-3">
              <div>
                <span className="text-xs font-medium text-gray-600">🥐 DESAYUNO</span>
                {getComidaTipo(comidas.desayuno)}
              </div>
              <div>
                <span className="text-xs font-medium text-gray-600">🍽️ COMIDA</span>
                {getComidaTipo(comidas.comida)}
              </div>
              <div>
                <span className="text-xs font-medium text-gray-600">🍽️ CENA</span>
                {getComidaTipo(comidas.cena)}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Tu Menú Semanal Generado por IA</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <p className="text-sm text-gray-600">Coste Total</p>
            <p className="text-xl font-bold text-verde">€{menu.total_coste.toFixed(2)}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <p className="text-sm text-gray-600">Presupuesto</p>
            <p className="text-xl font-bold text-blue-600">€{menu.presupuesto_utilizado.toFixed(2)}</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 text-center">
            <p className="text-sm text-gray-600">Personas</p>
            <p className="text-xl font-bold text-purple-600">€{menu.precio_promedio_comida.toFixed(2)}</p>
          </div>
          <div className="bg-orange-50 rounded-lg p-3 text-center">
            <p className="text-sm text-gray-600">Supermercados</p>
            <p className="text-xl font-bold text-orange-600">{menu.supermercados_usados.length}</p>
          </div>
        </div>
      </div>

      {getDiaComidas()}
    </div>
  );
}

export default MenuSemanal;