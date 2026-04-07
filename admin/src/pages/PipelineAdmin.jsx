import { useEffect, useState } from "react";
import api from "../services/api";

const PipelineAdmin = () => {
  const [monitor, setMonitor] = useState(null);

  useEffect(() => {
    api.get("/admin/pipeline").then((r) => setMonitor(r.data)).catch(() => setMonitor(null));
  }, []);

  return (
    <div className="bg-white p-4 rounded shadow space-y-2">
      <h2 className="text-xl font-semibold">Monitoring pipeline</h2>
      <p>Taux de succès (12 semaines): {monitor?.success_rate_12_weeks ?? 0}%</p>
      {(monitor?.executions || []).map((e, idx) => (
        <div key={idx} className="border rounded p-3">
          <p>Execution: {e.date} - {e.status}</p>
          <p>Tâches: {e.tasks?.join(", ")}</p>
        </div>
      ))}
    </div>
  );
};

export default PipelineAdmin;
