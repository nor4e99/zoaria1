'use client';

import { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface BMIIndicatorProps {
  normalized: number;        // 0–1
  status: 'underweight' | 'healthy' | 'overweight' | null;
  weight: number;
  minWeight: number;
  maxWeight: number;
  className?: string;
}

const STATUS_COLORS = {
  underweight: { arc: '#ef4444', label: 'Underweight', bg: 'bg-red-50', text: 'text-red-600', border: 'border-red-200' },
  healthy:     { arc: '#22c55e', label: 'Healthy',     bg: 'bg-green-50', text: 'text-green-600', border: 'border-green-200' },
  overweight:  { arc: '#f59e0b', label: 'Overweight',  bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200' },
};

export function BMIIndicator({ normalized, status, weight, minWeight, maxWeight, className }: BMIIndicatorProps) {
  const needleRef = useRef<SVGLineElement>(null);

  // Convert 0–1 to -130 to +130 degrees (260° arc)
  const angle = -130 + (normalized ?? 0.5) * 260;

  useEffect(() => {
    if (needleRef.current) {
      needleRef.current.style.transform = `rotate(${angle}deg)`;
    }
  }, [angle]);

  const cfg = status ? STATUS_COLORS[status] : STATUS_COLORS['healthy'];

  // Arc path helper
  function describeArc(cx: number, cy: number, r: number, startAngle: number, endAngle: number) {
    const rad = (deg: number) => ((deg - 90) * Math.PI) / 180;
    const x1 = cx + r * Math.cos(rad(startAngle));
    const y1 = cy + r * Math.sin(rad(startAngle));
    const x2 = cx + r * Math.cos(rad(endAngle));
    const y2 = cy + r * Math.sin(rad(endAngle));
    const large = endAngle - startAngle > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
  }

  const cx = 100, cy = 90, r = 70;

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <div className="relative">
        <svg width="200" height="130" viewBox="0 0 200 130">
          {/* Background arc (full range) */}
          <path
            d={describeArc(cx, cy, r, -40, 220)}
            fill="none" stroke="#e5f2e5" strokeWidth="12" strokeLinecap="round"
          />

          {/* Colored zone arcs */}
          {/* Underweight zone: -40 to 40 */}
          <path d={describeArc(cx, cy, r, -40, 40)}
            fill="none" stroke="#fecaca" strokeWidth="12" strokeLinecap="round" />
          {/* Healthy zone: 40 to 140 */}
          <path d={describeArc(cx, cy, r, 40, 140)}
            fill="none" stroke="#bbf7d0" strokeWidth="12" strokeLinecap="round" />
          {/* Overweight zone: 140 to 220 */}
          <path d={describeArc(cx, cy, r, 140, 220)}
            fill="none" stroke="#fde68a" strokeWidth="12" strokeLinecap="round" />

          {/* Active progress arc */}
          <path
            d={describeArc(cx, cy, r, -40, Math.min(-40 + normalized * 260, 220))}
            fill="none"
            stroke={cfg.arc}
            strokeWidth="12"
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.34,1.56,0.64,1)' }}
          />

          {/* Needle */}
          <g
            style={{
              transformOrigin: `${cx}px ${cy}px`,
              transform: `rotate(${angle}deg)`,
              transition: 'transform 0.8s cubic-bezier(0.34,1.56,0.64,1)',
            }}
          >
            <line
              ref={needleRef}
              x1={cx} y1={cy}
              x2={cx} y2={cy - r + 4}
              stroke={cfg.arc}
              strokeWidth="3"
              strokeLinecap="round"
            />
          </g>

          {/* Center dot */}
          <circle cx={cx} cy={cy} r="6" fill={cfg.arc} />
          <circle cx={cx} cy={cy} r="3" fill="white" />

          {/* Weight labels */}
          <text x="24" y="118" className="text-xs" fill="#9aa3a3" fontSize="10" textAnchor="middle">{minWeight}kg</text>
          <text x="176" y="118" className="text-xs" fill="#9aa3a3" fontSize="10" textAnchor="middle">{maxWeight}kg</text>
        </svg>

        {/* Center weight display */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
          <p className="font-display text-xl font-bold text-obsidian-900">{weight}kg</p>
        </div>
      </div>

      {/* Status badge */}
      {status && (
        <div className={cn('mt-2 px-4 py-1.5 rounded-full text-sm font-semibold border', cfg.bg, cfg.text, cfg.border)}>
          {cfg.label}
        </div>
      )}

      {/* Range labels */}
      <div className="flex gap-3 mt-3 text-xs text-obsidian-400">
        <span>Ideal: {minWeight}–{maxWeight} kg</span>
      </div>
    </div>
  );
}
