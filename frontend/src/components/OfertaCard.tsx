import { useState } from 'react';

function OfertaCard({ oferta }: { oferta: any }) {
  const descuento = oferta.descuento || 0;
  
  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden">
      <div className="relative">
        <img
          src={oferta.imagen || `https://picsum.photos/seed/${oferta.nombre}/300/200`}
          alt={oferta.nombre}
          className="w-full h-48 object-cover"
          onError={(e) => {
            (e.target as HTMLImageElement).src = 'https://picsum.photos/seed/default/300/200';
          }}
        />
        {descuento > 0 && (
          <div className="absolute top-2 right-2 bg-naranja text-white px-2 py-1 rounded-full text-sm font-bold">
            -{descuento}%
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">{oferta.nombre}</h3>
        <p className="text-sm text-gray-600 mb-2">Supermercado: {oferta.supermercado}</p>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-lg font-bold text-verde">€{oferta.precio.toFixed(2)}</span>
            {oferta.precio_original && (
              <span className="text-sm text-gray-500 line-through ml-2">€{oferta.precio_original.toFixed(2)}</span>
            )}
          </div>
          <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
            {oferta.categoria}
          </span>
        </div>
        <div className="mt-3 text-xs text-gray-500">
          <p>Ubicación: {oferta.ubicacion || 'No especificada'}</p>
          {oferta.fecha && <p>Fecha: {new Date(oferta.fecha).toLocaleDateString('es-ES')}</p>}
        </div>
      </div>
    </div>
  );
}

export default OfertaCard;