import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedAdmin from "./components/ProtectedAdmin";
import AnnoncesAdmin from "./pages/AnnoncesAdmin";
import DashboardAdmin from "./pages/DashboardAdmin";
import LoginAdmin from "./pages/LoginAdmin";
import OkrAdmin from "./pages/OkrAdmin";
import PipelineAdmin from "./pages/PipelineAdmin";
import UsersAdmin from "./pages/UsersAdmin";

const App = () => (
  <div className="min-h-screen">
    <Navbar />
    <main className="mx-auto max-w-7xl p-4 md:p-6">
      <Routes>
        <Route path="/login" element={<LoginAdmin />} />
        <Route path="/" element={<ProtectedAdmin><DashboardAdmin /></ProtectedAdmin>} />
        <Route path="/annonces" element={<ProtectedAdmin><AnnoncesAdmin /></ProtectedAdmin>} />
        <Route path="/users" element={<ProtectedAdmin><UsersAdmin /></ProtectedAdmin>} />
        <Route path="/okr" element={<ProtectedAdmin><OkrAdmin /></ProtectedAdmin>} />
        <Route path="/pipeline" element={<ProtectedAdmin><PipelineAdmin /></ProtectedAdmin>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </main>
  </div>
);

export default App;
