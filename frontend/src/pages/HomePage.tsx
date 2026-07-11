import { useEffect } from 'react';

function HomePage() {
  return (
    <div className="text-center py-12">
      <div className="max-w-3xl mx-auto">
        <div className="w-20 h-20 bg-verde rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <h1 className="text-4xl font-bold text-gray-800 mb-4">Ofertas Super + Menú Semanal IA</h1>
        <p className="text-xl text-gray-600 mb-8">
          Encuentra las mejores ofertas de supermercados cercanos (Mercadona, Lidl, Aldi, Dia, Carrefour, Alcampo)
          y genera un menú semanal con recetas de IA ajustado a un presupuesto.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-verde" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 18.657A8 8 0 1116.343 5.343 8 8 0 0117.657 18.657zM12 11a2 2 0 100-4 2 2 0 000 4z" />
              </svg>
            </div>
            <h3 className="font-semibold mb-2">6 Supermercados</h3>
            <p className="text-sm text-gray-600">Mercadona, Lidl, Aldi, Dia, Carrefour, Alcampo</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-naranja" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-semibold mb-2">Ajustado a Presupuesto</h3>
            <p className="text-sm text-gray-600">IA genera menús usando ofertas y tu presupuesto</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="font-semibold mb-2">Recetas IA</h3>
            <p className="text-sm text-gray-600">Menú semanal completo con desayuno, comida y cena</p>
          </div>
        </div>
        <div className="space-x-4">
          <a href="/ofertas" className="btn btn-green px-8 py-3">Ver Ofertas</a>
          <a href="/menu" className="btn btn-orange px-8 py-3">Generar Menú</a>
        </div>
      </div>
    </div>
  );
}

export default HomePage;