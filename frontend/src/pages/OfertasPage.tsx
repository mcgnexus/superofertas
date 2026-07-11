import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { OfertaFilters } from '../types';
import { ofertasApi } from '../services/api';

function OfertasPage() {
  const [ofertas, setOfertas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filtros, setFiltros] = useState<OfertaFilters>({});
  const navigate = useNavigate();

  const supermercados = ['Mercadona', 'Lidl', 'Aldi', 'Dia', 'Carrefour', 'Alcampo'];
  const categorias = ['frutas', 'verduras', 'lácteos', 'carnes', 'panadería', 'bebidas', 'limpieza', 'higiene'];

  const handleFilterChange = (newFilters: OfertaFilters) => {
    setFiltros(newFilters);
    fetchOfertas(newFilters);
  };

  const fetchOfertas = async (filters?: OfertaFilters) => {
    setLoading(true);
    setError('');
    try {
      const data = await ofertasApi.getOfertas(filters);
      setOfertas(data);
    } catch (err) {
      setError('Error al cargar ofertas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMenu = async () => {
    try {
      setLoading(true);
      const menuData = {
        presupuesto: 50,
        num_personas: 4,
        supermercados: ['Mercadona', 'Lidl'],
        restricciones: []
      };
      const menu = await ofertasApi.generarMenu(menuData);
      navigate('/menu', { state: { menu } });
    } catch (err) {
      setError('Error al generar menú');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOfertas(filtros);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Ofertas de Supermercados</h1>
        <button
          onClick={handleGenerateMenu}
          className="btn btn-green"
          disabled={loading}
        >
          Generar Menú Semanal
        </button>
      </div>

      <FiltrosOfertas onFilter={handleFilterChange} supermercados={supermercados} categorias={categorias} />

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-verde"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {ofertas.map((oferta: any) => (
            <OfertaCard key={oferta.id} oferta={oferta} />
          ))}
        </div>
      )}
    </div>
  );
}

export default OfertasPage;