import { Navigate } from "react-router-dom";

const ProtectedAdmin = ({ children }) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("admin_role");

  if (!token || role !== "admin") {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedAdmin;
