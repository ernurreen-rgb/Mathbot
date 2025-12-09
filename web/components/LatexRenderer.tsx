// components/LatexRenderer.tsx
"use client";

import { useEffect, useRef } from "react";

interface LatexRendererProps {
  text: string;
  className?: string;
}

export default function LatexRenderer({ text, className = "" }: LatexRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Dynamically import KaTeX only on client side
    const renderMath = async () => {
      if (typeof window !== "undefined" && containerRef.current) {
        try {
          const katex = (await import("katex")).default;
          
          const container = containerRef.current;
          container.innerHTML = "";

          // Check if text contains LaTeX delimiters
          const hasDelimiters = text.includes("$");
          
          const isBareLatex = !hasDelimiters && /\\[a-zA-Z*]+|\\[^a-zA-Z\\s]/.test(text);

          
          // If it's bare LaTeX from MathEditor, wrap it in $ delimiters
          const processedText = isBareLatex ? `$${text}$` : text;

          // Split text by LaTeX delimiters
          // Check for display math ($$) first, then inline math ($)
          const parts = processedText.split(/(\$\$[\s\S]*?\$\$|\$(?!\$)[^\$]+?\$(?!\$))/);
          
          parts.forEach((part) => {
            if (part.startsWith("$$") && part.endsWith("$$")) {
              // Display math (block)
              const math = part.slice(2, -2).trim();
              const span = document.createElement("div");
              span.className = "my-4";
              try {
                katex.render(math, span, {
                  displayMode: true,
                  throwOnError: false,
                });
                container.appendChild(span);
              } catch {
                span.textContent = part;
                container.appendChild(span);
              }
            } else if (part.startsWith("$") && part.endsWith("$") && !part.startsWith("$$")) {
              // Inline math (excluding display math)
              const math = part.slice(1, -1);
              const span = document.createElement("span");
              try {
                katex.render(math, span, {
                  displayMode: false,
                  throwOnError: false,
                });
                container.appendChild(span);
              } catch {
                span.textContent = part;
                container.appendChild(span);
              }
            } else {
              // Regular text
              const textNode = document.createTextNode(part);
              container.appendChild(textNode);
            }
          });
        } catch (error) {
          // Fallback to plain text if KaTeX fails to load
          if (containerRef.current) {
            containerRef.current.textContent = text;
          }
        }
      }
    };

    renderMath();
  }, [text]);

  return <div ref={containerRef} className={`whitespace-pre-wrap ${className}`} />;
}