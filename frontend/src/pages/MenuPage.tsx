import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import type { MenuSemanal } from '../types';
import { ofertasApi } from '../services/api';

function MenuPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    presupuesto: 50,
    num_personas: 4,
    supermercados: ['Mercadona'],
    restricciones: []
  });
  const navigate = useNavigate();
  const location = useLocation();
  const generatedMenu = location.state?.menu as MenuSemanal | undefined;

  const supermercados = ['Mercadona', 'Lidl', 'Aldi', 'Dia', 'Carrefour', 'Alcampo'];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'presupuesto' || name === 'num_personas' ? Number(value) : value
    }));
  };

  const handleSupermercadoChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = Array.from(e.target.selectedOptions, option => option.value);
    setFormData(prev => ({ ...prev, supermercados: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const menu = await ofertasApi.generarMenu(formData);
      navigate('/menu', { state: { menu } });
    } catch (err) {
      setError('Error al generar menú');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Generar Menú Semanal</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Formulario de Presupuesto</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Presupuesto (€)</label>
            <input
              type="number"
              name="presupuesto"
              value={formData.presupuesto}
              onChange={handleInputChange}
              min="10"
              max="500"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-verde"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Número de Personas</label>
            <input
              type="number"
              name="num_personas"
              value={formData.num_personas}
              onChange={handleInputChange}
              min="1"
              max="10"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-verde"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Supermercados (Ctrl+Click para seleccionar)</label>
            <select
              multiple
              name="supermercados"
              value={formData.supermercados}
              onChange={handleSupermercadoChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-verde"
            >
              {supermercados.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Mantén presionado Ctrl (o Cmd en Mac) para seleccionar múltiples</p>
          </div>
          <button
            type="submit"
            className="btn btn-green w-full"
            disabled={loading}
          >
            {loading ? 'Generando...' : 'Generar Menú con IA'}
          </button>
        </form>

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}
      </div>

      {generatedMenu && (
        <div>
          <h2 className="text-lg font-semibold mb-4">Menú Generado</h2>
          <MenuSemanal menu={generatedMenu} />
        </div>
      )}
    </div>
  );
}

export default MenuPage;