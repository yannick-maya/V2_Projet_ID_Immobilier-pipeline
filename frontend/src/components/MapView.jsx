import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const MapView = ({ points = [] }) => {
  const center = points.length ? [points[0].lat || 6.1375, points[0].lon || 1.2123] : [6.1375, 1.2123];

  return (
    <MapContainer center={center} zoom={12} className="h-96 w-full rounded-xl overflow-hidden">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {points.map((p, idx) => (
        <Marker key={idx} position={[p.lat || 6.1375, p.lon || 1.2123]}>
          <Popup>
            <div>
              <strong>{p.titre || p.zone}</strong>
              <br />
              {Number(p.prix || 0).toLocaleString()} FCFA
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapView;
