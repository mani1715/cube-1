import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import About from "./pages/About";
import Services from "./pages/Services";
import BookSession from "./pages/BookSession";
import Events from "./pages/Events";
import Blogs from "./pages/Blogs";
import Careers from "./pages/Careers";
import PsychologistPortal from "./pages/PsychologistPortal";
import Volunteer from "./pages/Volunteer";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";
import NotFound from "./pages/NotFound";
// Admin imports
import { AdminProvider } from "./contexts/AdminContext";
import AdminLayout from "./admin/AdminLayout";
import AdminDashboard from "./admin/pages/AdminDashboard";
import AdminSessions from "./admin/pages/AdminSessions";
import AdminEvents from "./admin/pages/AdminEvents";
import AdminBlogs from "./admin/pages/AdminBlogs";
import AdminPsychologists from "./admin/pages/AdminPsychologists";
import AdminVolunteers from "./admin/pages/AdminVolunteers";
import AdminJobs from "./admin/pages/AdminJobs";
import AdminContacts from "./admin/pages/AdminContacts";
import AdminSettings from "./admin/pages/AdminSettings";
import AdminLogs from "./admin/pages/AdminLogs";
import AdminErrors from "./admin/pages/AdminErrors";
import AdminLogin from "./admin/AdminLogin";
import AdminProtectedRoute from "./admin/AdminProtectedRoute";
import ErrorBoundary from "./admin/components/ErrorBoundary";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AdminProvider>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/about" element={<About />} />
            <Route path="/services" element={<Services />} />
            <Route path="/book-session" element={<BookSession />} />
            <Route path="/events" element={<Events />} />
            <Route path="/blogs" element={<Blogs />} />
            <Route path="/careers" element={<Careers />} />
            <Route path="/psychologist-portal" element={<PsychologistPortal />} />
            <Route path="/volunteer" element={<Volunteer />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/terms" element={<Terms />} />
            
            {/* Admin Login Route (Public) */}
            <Route path="/admin/login" element={<AdminLogin />} />
            
            {/* Protected Admin Routes */}
            <Route element={<AdminProtectedRoute />}>
              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<ErrorBoundary><AdminDashboard /></ErrorBoundary>} />
                <Route path="sessions" element={<ErrorBoundary><AdminSessions /></ErrorBoundary>} />
                <Route path="events" element={<ErrorBoundary><AdminEvents /></ErrorBoundary>} />
                <Route path="blogs" element={<ErrorBoundary><AdminBlogs /></ErrorBoundary>} />
                <Route path="psychologists" element={<ErrorBoundary><AdminPsychologists /></ErrorBoundary>} />
                <Route path="volunteers" element={<ErrorBoundary><AdminVolunteers /></ErrorBoundary>} />
                <Route path="jobs" element={<ErrorBoundary><AdminJobs /></ErrorBoundary>} />
                <Route path="contacts" element={<ErrorBoundary><AdminContacts /></ErrorBoundary>} />
                <Route path="logs" element={<ErrorBoundary><AdminLogs /></ErrorBoundary>} />
                <Route path="errors" element={<ErrorBoundary><AdminErrors /></ErrorBoundary>} />
                <Route path="settings" element={<ErrorBoundary><AdminSettings /></ErrorBoundary>} />
              </Route>
            </Route>
            
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AdminProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
