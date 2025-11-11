import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@/components/ui/tooltip";
import App from "./App.tsx";
import "./index.css";

// Create the client
const queryClient = new QueryClient();

// Find the root element
const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Failed to find the root element");

const root = createRoot(rootElement);

// Render the app
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);