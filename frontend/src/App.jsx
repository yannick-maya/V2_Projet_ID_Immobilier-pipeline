import { Navigate, Route, Routes } from "react-router-dom";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import BienDetail from "./pages/BienDetail";
import Dashboard from "./pages/Dashboard";
import Favoris from "./pages/Favoris";
import Home from "./pages/Home";
import Indice from "./pages/Indice";
import Login from "./pages/Login";
import Profil from "./pages/Profil";
import Register from "./pages/Register";
import Recherche from "./pages/Recherche";
import Simulateur from "./pages/Simulateur";

const App = () => (
  <div className="min-h-screen">
    <Navbar />
    <main className="max-w-7xl mx-auto px-4 py-6">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/recherche" element={<Recherche />} />
        <Route path="/annonce/:id" element={<BienDetail />} />
        <Route path="/indice" element={<Indice />} />
        <Route path="/simulateur" element={<Simulateur />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/favoris" element={<ProtectedRoute><Favoris /></ProtectedRoute>} />
        <Route path="/profil" element={<ProtectedRoute><Profil /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </main>
    <Footer />
  </div>
);

export default App;
