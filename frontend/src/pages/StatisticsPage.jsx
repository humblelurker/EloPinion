import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend } from 'chart.js';
import './StatisticsPage.css';
ChartJS.register(LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend);

const sampleProducts = [
  { id: 1, name: 'Producto A' },
  { id: 2, name: 'Producto B' },
];

const sampleEloHistory = {
  1: [
    { date: '2024-06-01', elo: 1200 },
    { date: '2024-06-10', elo: 1230 },
    { date: '2024-06-20', elo: 1280 },
  ],
  2: [
    { date: '2024-06-01', elo: 1100 },
    { date: '2024-06-10', elo: 1125 },
    { date: '2024-06-20', elo: 1140 },
  ]
};

export default function StatisticsPage() {
  const [selected, setSelected] = useState(sampleProducts[0].id);
  const [data, setData] = useState([]);

  useEffect(() => {
    setData(sampleEloHistory[selected] || []);
  }, [selected]);

  const chartData = {
    labels: data.map(point => point.date),
    datasets: [
      {
        label: 'Elo a lo largo del tiempo',
        data: data.map(point => point.elo),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.3)',
        tension: 0.3
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Historial de Elo del Producto' }
    }
  };

  return (
    <div className="stats-card">
      <h2>Estadísticas</h2>
      <label>Selecciona un producto:</label>
      <select onChange={e => setSelected(Number(e.target.value))} value={selected}>
        {sampleProducts.map(p => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>
      <Line data={chartData} options={chartOptions} />
      <h3 style={{ marginTop: '2rem' }}>Top productos</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
            <thead>
            <tr style={{ background: '#000' }}>
                <th style={{ padding: '0.5rem', textAlign: 'left', color: '#fff' }}>#</th>
                <th style={{ padding: '0.5rem', textAlign: 'left', color: '#fff' }}>Nombre</th>
                <th style={{ padding: '0.5rem', textAlign: 'left', color: '#fff' }}>Elo</th>
                <th style={{ padding: '0.5rem', textAlign: 'left', color: '#fff' }}>Categoría</th>
            </tr>
            </thead>
            <tbody>
            {[
                { name: 'Producto A', elo: 1280, cat: 'Bebidas' },
                { name: 'Producto B', elo: 1140, cat: 'Snacks' },
                { name: 'Producto C', elo: 1095, cat: 'Limpieza' },
            ].map((p, i) => (
                <tr key={i} style={{ borderTop: '1px solid #eee', backgroundColor: '#fff', color: '#222' }}>
                <td style={{ padding: '0.5rem' }}>{i + 1}</td>
                <td style={{ padding: '0.5rem' }}>{p.name}</td>
                <td style={{ padding: '0.5rem' }}>{p.elo}</td>
                <td style={{ padding: '0.5rem' }}>{p.cat}</td>
                </tr>
            ))}
            </tbody>
        </table>
    </div>
  );
}