"use client";

import { useEffect, useMemo, useRef } from "react";
import { useWeather } from "@/components/weather-provider";

interface Particle {
  x: number;
  y: number;
  speed: number;
  opacity: number;
  size: number;
  drift: number;
  wobble: number;
  wobbleSpeed: number;
}

function createRainDrops(count: number): Particle[] {
  return Array.from({ length: count }, () => ({
    x: Math.random() * 100,
    y: Math.random() * -100,
    speed: 1.5 + Math.random() * 2.5,
    opacity: 0.15 + Math.random() * 0.35,
    size: 1 + Math.random() * 2,
    drift: -0.3 + Math.random() * 0.2,
    wobble: 0,
    wobbleSpeed: 0,
  }));
}

function createSnowflakes(count: number): Particle[] {
  return Array.from({ length: count }, () => ({
    x: Math.random() * 100,
    y: Math.random() * -100,
    speed: 0.2 + Math.random() * 0.5,
    opacity: 0.3 + Math.random() * 0.5,
    size: 2 + Math.random() * 4,
    drift: 0,
    wobble: Math.random() * Math.PI * 2,
    wobbleSpeed: 0.01 + Math.random() * 0.02,
  }));
}

function createClouds(count: number): Particle[] {
  return Array.from({ length: count }, () => ({
    x: Math.random() * 120 - 10,
    y: 5 + Math.random() * 30,
    speed: 0.005 + Math.random() * 0.015,
    opacity: 0.04 + Math.random() * 0.08,
    size: 80 + Math.random() * 160,
    drift: 0,
    wobble: 0,
    wobbleSpeed: 0,
  }));
}

function createSunRays(count: number): Particle[] {
  return Array.from({ length: count }, () => ({
    x: 20 + Math.random() * 60,
    y: -5 + Math.random() * 20,
    speed: 0,
    opacity: 0.02 + Math.random() * 0.04,
    size: 200 + Math.random() * 300,
    drift: 0,
    wobble: Math.random() * Math.PI * 2,
    wobbleSpeed: 0.003 + Math.random() * 0.005,
  }));
}

export function WeatherBackground() {
  const weather = useWeather();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animFrameRef = useRef<number>(0);

  const condition = weather.condition;
  const topOverlayClass =
    condition === "thunderstorm"
      ? "from-slate-700/35 via-slate-600/10 to-transparent"
      : condition === "rain" || condition === "drizzle"
        ? "from-slate-600/25 via-slate-500/10 to-transparent"
        : condition === "cloudy" || condition === "partly_cloudy" || condition === "fog"
          ? "from-amber-900/12 via-amber-900/4 to-transparent"
          : "from-amber-400/8 via-transparent to-transparent";

  const particles = useMemo(() => {
    switch (condition) {
      case "rain":
      case "drizzle":
        return createRainDrops(condition === "drizzle" ? 60 : 120);
      case "thunderstorm":
        return createRainDrops(180);
      case "snow":
        return createSnowflakes(80);
      case "cloudy":
      case "partly_cloudy":
      case "fog":
        return createClouds(6);
      case "clear":
        return createSunRays(5);
      default:
        return createSunRays(3);
    }
  }, [condition]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let w = 0;
    let h = 0;

    function resize() {
      if (!canvas) return;
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = w;
      canvas.height = h;
    }
    resize();
    window.addEventListener("resize", resize);

    function drawRain(p: Particle) {
      if (!ctx) return;
      const px = (p.x / 100) * w;
      const py = (p.y / 100) * h;
      ctx.beginPath();
      ctx.strokeStyle = `rgba(174, 194, 224, ${p.opacity})`;
      ctx.lineWidth = p.size * 0.5;
      ctx.lineCap = "round";
      ctx.moveTo(px, py);
      ctx.lineTo(px + p.drift * 8, py + p.size * 12);
      ctx.stroke();
    }

    function drawSnow(p: Particle) {
      if (!ctx) return;
      const px = (p.x / 100) * w;
      const py = (p.y / 100) * h;
      ctx.beginPath();
      ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fill();
    }

    function drawCloud(p: Particle) {
      if (!ctx) return;
      const px = (p.x / 100) * w;
      const py = (p.y / 100) * h;
      const gradient = ctx.createRadialGradient(px, py, 0, px, py, p.size);
      gradient.addColorStop(0, `rgba(180, 180, 200, ${p.opacity})`);
      gradient.addColorStop(1, `rgba(180, 180, 200, 0)`);
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fill();
    }

    function drawSunRay(p: Particle) {
      if (!ctx) return;
      const px = (p.x / 100) * w;
      const py = (p.y / 100) * h;
      const pulse = Math.sin(p.wobble) * 0.3 + 0.7;
      const gradient = ctx.createRadialGradient(px, py, 0, px, py, p.size * pulse);
      gradient.addColorStop(0, `rgba(255, 220, 120, ${p.opacity * pulse})`);
      gradient.addColorStop(0.5, `rgba(255, 200, 80, ${p.opacity * 0.3 * pulse})`);
      gradient.addColorStop(1, `rgba(255, 180, 60, 0)`);
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(px, py, p.size * pulse, 0, Math.PI * 2);
      ctx.fill();
    }

    let flashTimer = 0;
    let flashOpacity = 0;

    function animate() {
      if (!ctx) return;
      ctx.clearRect(0, 0, w, h);

      if (condition === "thunderstorm") {
        flashTimer++;
        if (flashTimer > 200 + Math.random() * 400) {
          flashOpacity = 0.15 + Math.random() * 0.15;
          flashTimer = 0;
        }
        if (flashOpacity > 0) {
          ctx.fillStyle = `rgba(255, 255, 255, ${flashOpacity})`;
          ctx.fillRect(0, 0, w, h);
          flashOpacity *= 0.85;
          if (flashOpacity < 0.005) flashOpacity = 0;
        }
      }

      for (const p of particles) {
        switch (condition) {
          case "rain":
          case "drizzle":
          case "thunderstorm":
            p.y += p.speed;
            p.x += p.drift;
            if (p.y > 105) {
              p.y = Math.random() * -10;
              p.x = Math.random() * 100;
            }
            drawRain(p);
            break;
          case "snow":
            p.y += p.speed;
            p.wobble += p.wobbleSpeed;
            p.x += Math.sin(p.wobble) * 0.15;
            if (p.y > 105) {
              p.y = Math.random() * -5;
              p.x = Math.random() * 100;
            }
            drawSnow(p);
            break;
          case "cloudy":
          case "partly_cloudy":
          case "fog":
            p.x += p.speed;
            if (p.x > 115) p.x = -15;
            drawCloud(p);
            break;
          default:
            p.wobble += p.wobbleSpeed;
            drawSunRay(p);
            break;
        }
      }

      animFrameRef.current = requestAnimationFrame(animate);
    }

    animFrameRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animFrameRef.current);
    };
  }, [condition, particles]);

  return (
    <>
      <canvas
        ref={canvasRef}
        className="pointer-events-none fixed inset-0 z-0"
        aria-hidden="true"
      />
      <div
        aria-hidden="true"
        className={`pointer-events-none fixed inset-x-0 top-0 z-0 h-56 bg-gradient-to-b ${topOverlayClass}`}
      />
    </>
  );
}
