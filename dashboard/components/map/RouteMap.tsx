"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from "react-leaflet";
import type { ProcessedRoute } from "@/lib/types";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix for default marker icons in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const BAKU_CENTER: [number, number] = [40.4093, 49.8671];

interface RouteMapProps {
  routes: ProcessedRoute[];
  selectedRoute: ProcessedRoute | null;
  onRouteClick?: (route: ProcessedRoute) => void;
}

function MapUpdater({ routes }: { routes: ProcessedRoute[] }) {
  const map = useMap();

  useEffect(() => {
    if (routes.length > 0) {
      // Calculate bounds of all routes
      const bounds: [number, number][] = [];
      routes.forEach((route) => {
        route.stops?.forEach((stop) => {
          const lat = parseFloat(stop.stop?.latitude || "0");
          const lon = parseFloat(stop.stop?.longitude || "0");
          if (lat && lon && !isNaN(lat) && !isNaN(lon) && lat !== 0 && lon !== 0) {
            bounds.push([lat, lon]);
          }
        });

        // Also add flowCoordinates to bounds
        route.routes?.forEach((variant) => {
          variant.flowCoordinates?.forEach((coord) => {
            if (coord && coord.lat && coord.lon && !isNaN(coord.lat) && !isNaN(coord.lon)) {
              bounds.push([coord.lat, coord.lon]);
            }
          });
        });
      });

      if (bounds.length > 0) {
        map.fitBounds(L.latLngBounds(bounds), { padding: [50, 50] });
      }
    }
  }, [routes, map]);

  return null;
}

export default function RouteMap({ routes, selectedRoute, onRouteClick }: RouteMapProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <div className="text-gray-500">Loading map...</div>
      </div>
    );
  }

  // Show a sample of routes with valid coordinates initially to avoid empty map
  const displayRoutes = selectedRoute
    ? [selectedRoute]
    : routes
        .filter((route) => {
          // Only show routes that have valid flowCoordinates
          return route.routes?.some((variant) =>
            variant.flowCoordinates &&
            variant.flowCoordinates.length > 0 &&
            variant.flowCoordinates.some((coord) =>
              coord && coord.lat && coord.lon && !isNaN(coord.lat) && !isNaN(coord.lon)
            )
          );
        })
        .slice(0, 30); // Limit to 30 routes for better initial performance

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={BAKU_CENTER}
        zoom={11}
        style={{ height: "100%", width: "100%" }}
        className="z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapUpdater routes={displayRoutes} />

      {displayRoutes.map((route) => {
        // Draw route polylines from flowCoordinates
        const routeLines = route.routes?.map((variant, idx) => {
          if (!variant.flowCoordinates || variant.flowCoordinates.length === 0) return null;

          const coordinates: [number, number][] = variant.flowCoordinates
            .filter((coord) => coord && coord.lat && coord.lon && !isNaN(coord.lat) && !isNaN(coord.lon))
            .map((coord) => [coord.lat, coord.lon]);

          // Skip if no valid coordinates
          if (coordinates.length === 0) return null;

          const color = selectedRoute ? "#3b82f6" : getColorBySpeed(route.avgSpeed);

          return (
            <Polyline
              key={`${route.id}-${idx}`}
              positions={coordinates}
              pathOptions={{
                color,
                weight: selectedRoute ? 5 : 3,
                opacity: selectedRoute ? 0.9 : 0.6,
              }}
              eventHandlers={{
                click: () => onRouteClick?.(route),
              }}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold text-lg">Bus {route.number}</h3>
                  <p className="text-sm text-gray-600">{route.firstPoint} → {route.lastPoint}</p>
                  <div className="mt-2 space-y-1 text-sm">
                    <p><span className="font-semibold">Speed:</span> {route.avgSpeed.toFixed(1)} km/h</p>
                    <p><span className="font-semibold">Length:</span> {route.routLength} km</p>
                    <p><span className="font-semibold">Stops:</span> {route.stopCount}</p>
                    <p><span className="font-semibold">Carrier:</span> {route.carrier}</p>
                  </div>
                </div>
              </Popup>
            </Polyline>
          );
        });

        // Draw stops as markers (only for selected route to avoid clutter)
        const stopMarkers = selectedRoute && route.stops?.map((stop, stopIdx) => {
          const lat = parseFloat(stop.stop?.latitude || "0");
          const lon = parseFloat(stop.stop?.longitude || "0");

          if (!lat || !lon || isNaN(lat) || isNaN(lon) || lat === 0 || lon === 0) return null;

          const isHub = stop.stop?.isTransportHub;
          const isFirst = stopIdx === 0;
          const isLast = stopIdx === (route.stops?.length || 0) - 1;

          // Larger and more visible markers
          const markerSize = isHub ? 24 : isFirst || isLast ? 20 : 16;
          const bgColor = isHub ? "#ef4444" : isFirst ? "#10b981" : isLast ? "#f59e0b" : "#3b82f6";
          const pulseAnimation = (isHub || isFirst || isLast) ? `
            @keyframes pulse {
              0%, 100% { transform: scale(1); opacity: 1; }
              50% { transform: scale(1.2); opacity: 0.8; }
            }
          ` : '';

          const icon = L.divIcon({
            className: "custom-stop-marker",
            html: `
              <style>
                ${pulseAnimation}
                .marker-outer {
                  animation: ${(isHub || isFirst || isLast) ? 'pulse 2s ease-in-out infinite' : 'none'};
                }
              </style>
              <div class="marker-outer" style="
                background-color: ${bgColor};
                width: ${markerSize}px;
                height: ${markerSize}px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.4), 0 0 0 2px ${bgColor}40;
                cursor: pointer;
                transition: all 0.2s ease;
              "></div>
            `,
            iconSize: [markerSize, markerSize],
            iconAnchor: [markerSize / 2, markerSize / 2],
          });

          return (
            <Marker key={stop.id} position={[lat, lon]} icon={icon}>
              <Popup>
                <div className="p-2 min-w-[200px]">
                  <h4 className="font-bold text-gray-900 mb-2">{stop.stop?.name}</h4>
                  <div className="space-y-1">
                    <p className="text-xs text-gray-600">
                      <span className="font-semibold">Distance:</span> {stop.totalDistance.toFixed(1)} km from start
                    </p>
                    {isFirst && (
                      <p className="text-xs text-green-600 font-semibold bg-green-50 px-2 py-1 rounded">
                        🚩 Starting Point
                      </p>
                    )}
                    {isLast && (
                      <p className="text-xs text-orange-600 font-semibold bg-orange-50 px-2 py-1 rounded">
                        🏁 End Point
                      </p>
                    )}
                    {isHub && (
                      <p className="text-xs text-red-600 font-semibold bg-red-50 px-2 py-1 rounded">
                        🔄 Transport Hub
                      </p>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        });

        return (
          <div key={route.id}>
            {routeLines}
            {stopMarkers}
          </div>
        );
      })}
      </MapContainer>

      {/* Map Legend */}
      {selectedRoute && (
        <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-3 z-[1000] max-w-[200px]">
          <h4 className="text-xs font-bold text-gray-900 mb-2">Stop Types</h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 rounded-full bg-green-500 border-2 border-white shadow-md flex-shrink-0"></div>
              <span className="text-xs text-gray-700">Start Point</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 rounded-full bg-orange-500 border-2 border-white shadow-md flex-shrink-0"></div>
              <span className="text-xs text-gray-700">End Point</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-red-500 border-2 border-white shadow-md flex-shrink-0"></div>
              <span className="text-xs text-gray-700">Transport Hub</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-blue-500 border-2 border-white shadow-md flex-shrink-0"></div>
              <span className="text-xs text-gray-700">Regular Stop</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function getColorBySpeed(speed: number): string {
  if (speed >= 37) return "#22c55e"; // Green - fast
  if (speed >= 36.5) return "#eab308"; // Yellow - medium
  return "#ef4444"; // Red - slow
}
