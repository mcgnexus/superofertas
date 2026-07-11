import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import OfertasPage from './pages/OfertasPage';
import MenuPage from './pages/MenuPage';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/ofertas" element={<OfertasPage />} />
          <Route path="/menu" element={<MenuPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;