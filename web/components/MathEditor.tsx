// web/components/MathEditor.tsx
"use client";

import { useEffect, useRef } from "react";

interface MathEditorProps {
  value: string;
  onChange: (latex: string) => void;
  placeholder?: string;
  className?: string;
}

export default function MathEditor({ value, onChange, placeholder, className }: MathEditorProps) {
  const mathFieldRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Dynamically import MathLive only on client side
    import("mathlive").then((MathLive) => {
      if (containerRef.current && !mathFieldRef.current) {
        // Create math-field element
        const mf = new MathLive.MathfieldElement();
        
        // Add event listener for input changes
        mf.addEventListener("input", () => {
          onChange(mf.value);
        });
        
        mathFieldRef.current = mf;
        containerRef.current.appendChild(mf);
        
        // Set initial value
        if (value) {
          mf.value = value;
        }
      }
    });

    return () => {
      // Cleanup
      if (mathFieldRef.current && containerRef.current && containerRef.current.contains(mathFieldRef.current)) {
        containerRef.current.removeChild(mathFieldRef.current);
        mathFieldRef.current = null;
      }
    };
  }, [onChange]);

  // Update value when prop changes
  useEffect(() => {
    if (mathFieldRef.current && mathFieldRef.current.value !== value) {
      mathFieldRef.current.value = value || "";
    }
  }, [value]);

  return (
    <div className={className}>
      <div
        ref={containerRef}
        className="border-2 border-gray-300 rounded-lg p-3 min-h-[60px] focus-within:border-blue-500 bg-white"
        style={{ fontSize: "18px" }}
      />
      {placeholder && !value && (
        <p className="text-sm text-gray-400 mt-1">{placeholder}</p>
      )}
    </div>
  );
}
