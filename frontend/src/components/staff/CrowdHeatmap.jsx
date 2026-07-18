/**
 * CrowdHeatmap — SVG-based stadium heatmap visualization.
 * Color-codes gates by crowd density (green → yellow → red).
 * No heavy charting library — hand-rolled SVG for repo size.
 */

import './CrowdHeatmap.css';

/**
 * Map density percentage to a color (green → yellow → orange → red).
 * @param {number} density - 0-100 density percentage
 * @returns {string} HSL color string
 */
function densityToColor(density) {
  // Hue: 120 (green) → 60 (yellow) → 30 (orange) → 0 (red)
  const hue = Math.max(0, 120 - density * 1.2);
  const saturation = 70 + density * 0.2;
  const lightness = 50 - density * 0.1;
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

/**
 * Gate positions on the stadium SVG (normalized 0-1, mapped to SVG viewBox).
 */
const GATE_POSITIONS = {
  A: { x: 155, y: 40, labelY: 25 },
  B: { x: 345, y: 40, labelY: 25 },
  C: { x: 460, y: 155, labelY: 140 },
  D: { x: 460, y: 345, labelY: 330 },
  E: { x: 345, y: 460, labelY: 480 },
  F: { x: 155, y: 460, labelY: 480 },
  G: { x: 40, y: 345, labelY: 330 },
  H: { x: 40, y: 155, labelY: 140 },
};

export default function CrowdHeatmap({ gates }) {
  if (!gates || gates.length === 0) {
    return <div className="heatmap-empty">No crowd data available</div>;
  }

  return (
    <div className="heatmap-container" role="img" aria-label="Stadium crowd density heatmap">
      <svg viewBox="0 0 500 500" className="heatmap-svg" xmlns="http://www.w3.org/2000/svg">
        {/* Stadium Outline — Rounded rectangle representing the stadium bowl */}
        <rect
          x="80"
          y="80"
          width="340"
          height="340"
          rx="60"
          ry="60"
          fill="none"
          stroke="var(--color-border)"
          strokeWidth="2"
          className="stadium-outline"
        />

        {/* Inner pitch */}
        <rect
          x="150"
          y="150"
          width="200"
          height="200"
          rx="10"
          ry="10"
          fill="rgba(0, 184, 148, 0.08)"
          stroke="rgba(0, 184, 148, 0.3)"
          strokeWidth="1"
          strokeDasharray="5,5"
        />

        {/* Pitch label */}
        <text
          x="250"
          y="250"
          textAnchor="middle"
          dominantBaseline="middle"
          fill="var(--color-text-muted)"
          fontSize="12"
          fontFamily="var(--font-display)"
        >
          PITCH
        </text>

        {/* Gate density circles */}
        {gates.map((gate) => {
          const pos = GATE_POSITIONS[gate.gate_id];
          if (!pos) return null;

          const color = densityToColor(gate.density_percent);
          const radius = 25 + gate.density_percent * 0.15;
          const glowRadius = radius + 8;

          return (
            <g key={gate.gate_id} className="gate-group">
              {/* Glow effect */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={glowRadius}
                fill={color}
                opacity={0.15}
                className="gate-glow"
              />

              {/* Main density circle */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={radius}
                fill={color}
                opacity={0.6}
                stroke={color}
                strokeWidth="2"
                className="gate-circle"
              >
                <title>
                  Gate {gate.gate_id}: {gate.density_percent}% capacity, Queue: {gate.queue_length}{' '}
                  people, Wait: {gate.estimated_wait_minutes} min
                </title>
              </circle>

              {/* Gate label */}
              <text
                x={pos.x}
                y={pos.y - 2}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="white"
                fontSize="13"
                fontWeight="800"
                fontFamily="var(--font-display)"
                className="gate-label"
              >
                {gate.gate_id}
              </text>

              {/* Density percentage */}
              <text
                x={pos.x}
                y={pos.y + 13}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="white"
                fontSize="9"
                fontWeight="600"
                fontFamily="var(--font-body)"
                opacity="0.9"
              >
                {Math.round(gate.density_percent)}%
              </text>
            </g>
          );
        })}

        {/* Legend */}
        <g transform="translate(10, 470)">
          <rect x="0" y="0" width="15" height="8" rx="2" fill="hsl(120, 70%, 50%)" />
          <text x="18" y="8" fill="var(--color-text-muted)" fontSize="8">
            Low
          </text>

          <rect x="50" y="0" width="15" height="8" rx="2" fill="hsl(60, 78%, 46%)" />
          <text x="68" y="8" fill="var(--color-text-muted)" fontSize="8">
            Medium
          </text>

          <rect x="115" y="0" width="15" height="8" rx="2" fill="hsl(30, 84%, 43%)" />
          <text x="133" y="8" fill="var(--color-text-muted)" fontSize="8">
            High
          </text>

          <rect x="165" y="0" width="15" height="8" rx="2" fill="hsl(0, 90%, 40%)" />
          <text x="183" y="8" fill="var(--color-text-muted)" fontSize="8">
            Critical
          </text>
        </g>
      </svg>

      {/* Gate detail table for screen readers */}
      <table className="sr-only" aria-label="Gate density details">
        <thead>
          <tr>
            <th>Gate</th>
            <th>Density</th>
            <th>Queue</th>
            <th>Wait Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {gates.map((gate) => (
            <tr key={gate.gate_id}>
              <td>Gate {gate.gate_id}</td>
              <td>{gate.density_percent}%</td>
              <td>{gate.queue_length} people</td>
              <td>{gate.estimated_wait_minutes} minutes</td>
              <td>{gate.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
