import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { OfertaFilters } from '../types';
import { ofertasApi } from '../services/api';
import FiltrosOfertas from '../components/FiltrosOfertas';
import OfertaCard from '../components/OfertaCard';

function OfertasPage() {
  const [ofertas, setOfertas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filtros, setFiltros] = useState<OfertaFilters>({});
  const [scrapeMsg, setScrapeMsg] = useState('');
  const [scrapeLoading, setScrapeLoading] = useState(false);
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

  const handleScrapeMercadona = async () => {
    setScrapeLoading(true);
    setScrapeMsg('');
    try {
      const res = await ofertasApi.scrapeMercadona();
      setScrapeMsg(`✅ ${res.mensaje || 'Mercadona scrapeado'}`);
      fetchOfertas(filtros);
    } catch (err: any) {
      setScrapeMsg(`❌ Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setScrapeLoading(false);
    }
  };

  const handleScrapeAll = async () => {
    setScrapeLoading(true);
    setScrapeMsg('');
    try {
      const resultados = await ofertasApi.scrapeAll();
      const msgs = Object.entries(resultados).map(([s, r]) => `${s}: ${r}`);
      setScrapeMsg(`✅ ${msgs.join(' | ')}`);
      fetchOfertas(filtros);
    } catch (err: any) {
      setScrapeMsg(`❌ Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setScrapeLoading(false);
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

      <div className="flex flex-wrap gap-3 items-center">
        <button
          onClick={handleScrapeMercadona}
          disabled={scrapeLoading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
        >
          {scrapeLoading ? 'Scrapeando...' : '🔄 Scrapear Mercadona'}
        </button>
        <button
          onClick={handleScrapeAll}
          disabled={scrapeLoading}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
        >
          {scrapeLoading ? 'Scrapeando...' : '🔄 Scrapear Todos'}
        </button>
        {scrapeMsg && (
          <span className="text-sm text-gray-700 ml-2">{scrapeMsg}</span>
        )}
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
