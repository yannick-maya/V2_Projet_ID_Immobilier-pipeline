import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import AnnoncesAdmin from "./pages/AnnoncesAdmin";
import DashboardAdmin from "./pages/DashboardAdmin";
import OkrAdmin from "./pages/OkrAdmin";
import PipelineAdmin from "./pages/PipelineAdmin";
import UsersAdmin from "./pages/UsersAdmin";

const App = () => (
  <div className="min-h-screen">
    <Navbar />
    <main className="max-w-7xl mx-auto p-6">
      <Routes>
        <Route path="/" element={<DashboardAdmin />} />
        <Route path="/annonces" element={<AnnoncesAdmin />} />
        <Route path="/users" element={<UsersAdmin />} />
        <Route path="/okr" element={<OkrAdmin />} />
        <Route path="/pipeline" element={<PipelineAdmin />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </main>
  </div>
);

export default App;
