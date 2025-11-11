import { Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import Index from "./pages/Index";
import Auth from "./pages/Auth";
import Feedback from "./pages/Feedback";
import Admin from "./pages/Admin";
import NotFound from "./pages/NotFound";

const App = () => {
  return (
    <>
      <Toaster />
      <Sonner />
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/feedback" element={<Feedback />} />
        <Route path="/admin" element={<Admin />} />
        {/* This catch-all route MUST be last */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
};

export default App;