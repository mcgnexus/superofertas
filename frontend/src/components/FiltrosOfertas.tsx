import { useState } from 'react';
import type { Oferta } from '../types';

interface FiltrosOfertasProps {
  onFilter: (filters: any) => void;
  supermercados: string[];
  categorias: string[];
}

function FiltrosOfertas({ onFilter, supermercados, categorias }: FiltrosOfertasProps) {
  const [supermercado, setSupermercado] = useState('');
  const [categoria, setCategoria] = useState('');
  const [precioMax, setPrecioMax] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilter({
      supermercado: supermercado || undefined,
      categoria: categoria || undefined,
      precio_max: precioMax ? Number(precioMax) : undefined
    });
  };

  const handleReset = () => {
    setSupermercado('');
    setCategoria('');
    setPrecioMax('');
    onFilter({});
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Supermercado</label>
          <select
            value={supermercado}
            onChange={(e) => setSupermercado(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-verde"
          >
            <option value="">Todos</option>
            {supermercados.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
          <select
            value={categoria}
            onChange={(e) => setCategoria(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-verde"
          >
            <option value="">Todas</option>
            {categorias.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Precio Máximo</label>
          <input
            type="number"
            value={precioMax}
            onChange={(e) => setPrecioMax(e.target.value)}
            placeholder="€ máximo"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-verde"
          />
        </div>
        <div className="flex gap-2">
          <button
            type="submit"
            className="btn btn-green flex-1"
          >
            Filtrar
          </button>
          <button
            type="button"
            onClick={handleReset}
            className="btn bg-gray-300 text-gray-700 hover:bg-gray-400 flex-1"
          >
            Limpiar
          </button>
        </div>
      </div>
    </form>
  );
}

export default FiltrosOfertas;