import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "@/api/axiosInstance";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { BarChart3, TrendingUp, Users, AlertCircle, ArrowLeft, Settings } from "lucide-react";
import DriverList from "@/components/admin/DriverList";
import DriverAnalytics from "@/components/admin/DriverAnalytics";
import { toast } from "@/components/ui/use-toast";

interface Config {
  alert_threshold: number;
  ema_alpha: number;
  alert_throttle_minutes: number;
  feature_flags: Record<string, boolean>;
}

interface Stats {
  totalDrivers: number;
  averageScore: number;
  totalFeedback: number;
  alertsToday: number;
}

const Admin = () => {
  const navigate = useNavigate();

  const [stats, setStats] = useState<Stats | null>(null);
  const [config, setConfig] = useState<Config | null>(null);
  const [selectedFeature, setSelectedFeature] = useState<string>("DRIVER");
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showConfig, setShowConfig] = useState(false);

  // Local editable config state
  const [editableConfig, setEditableConfig] = useState<Partial<Config>>({});

  // Fetch config + stats
  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          navigate("/login");
          return;
        }

        // Check admin access
        const configRes = await api.get("/admin/config");
        setConfig(configRes.data);
        setEditableConfig(configRes.data);

        // Fetch dashboard stats (optional endpoint)
        try {
          const statsRes = await api.get("/admin/stats");
          setStats(statsRes.data);
        } catch {
          setStats({
            totalDrivers: 0,
            averageScore: 0,
            totalFeedback: 0,
            alertsToday: 0,
          });
        }
      } catch (err) {
        console.error("Admin access denied or fetch error:", err);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [navigate]);

  // Handle config updates
  const handleSaveConfig = async () => {
    try {
      await api.post("/admin/config", editableConfig);
      toast({ title: "Configuration updated successfully" });
      setShowConfig(false);
      const newConfig = await api.get("/admin/config");
      setConfig(newConfig.data);
    } catch (err) {
      toast({ title: "Failed to update config", variant: "destructive" });
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-muted-foreground">
        Loading admin dashboard...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Navbar */}
      <nav className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate("/feedback")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">Admin Dashboard</h1>
            </div>
          </div>

          <Button variant="outline" onClick={() => setShowConfig(!showConfig)}>
            <Settings className="h-4 w-4 mr-2" />
            {showConfig ? "Hide Config" : "Edit Config"}
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Config Editor */}
        {showConfig && config && (
          <Card className="p-4">
            <CardHeader>
              <CardTitle>System Configuration</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <Label>Alert Threshold</Label>
                <Input
                  type="number"
                  value={editableConfig.alert_threshold}
                  onChange={(e) =>
                    setEditableConfig((prev) => ({
                      ...prev,
                      alert_threshold: parseFloat(e.target.value),
                    }))
                  }
                />
              </div>

              <div>
                <Label>EMA Alpha</Label>
                <Input
                  type="number"
                  value={editableConfig.ema_alpha}
                  onChange={(e) =>
                    setEditableConfig((prev) => ({
                      ...prev,
                      ema_alpha: parseFloat(e.target.value),
                    }))
                  }
                />
              </div>

              <div>
                <Label>Alert Throttle (min)</Label>
                <Input
                  type="number"
                  value={editableConfig.alert_throttle_minutes}
                  onChange={(e) =>
                    setEditableConfig((prev) => ({
                      ...prev,
                      alert_throttle_minutes: parseFloat(e.target.value),
                    }))
                  }
                />
              </div>

              <div className="flex items-end justify-end">
                <Button onClick={handleSaveConfig}>Save Config</Button>
              </div>
            </CardContent>

            {/* Feature flags */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4">
              {Object.entries(config.feature_flags).map(([key, value]) => (
                <div key={key} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={editableConfig.feature_flags?.[key] ?? value}
                    onChange={(e) =>
                      setEditableConfig((prev) => ({
                        ...prev,
                        feature_flags: {
                          ...prev.feature_flags,
                          [key]: e.target.checked,
                        },
                      }))
                    }
                  />
                  <Label>{key}</Label>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Overview Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <OverviewCard title="Total Drivers" value={stats.totalDrivers} icon={<Users />} subtitle="Active in system" />
            <OverviewCard title="Average Score" value={stats.averageScore.toFixed(2)} icon={<TrendingUp />} subtitle="+0.2 from last week" />
            <OverviewCard title="Total Feedback" value={stats.totalFeedback} icon={<BarChart3 />} subtitle="All time" />
            <OverviewCard title="Alerts Today" value={stats.alertsToday} icon={<AlertCircle />} subtitle="Require attention" />
          </div>
        )}

        {/* Feature Flag + Entity Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Select Feature Category</CardTitle>
          </CardHeader>
          <CardContent className="flex gap-4 items-center">
            <Select value={selectedFeature} onValueChange={setSelectedFeature}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Select feature" />
              </SelectTrigger>
              <SelectContent>
                {config &&
                  Object.keys(config.feature_flags).map((flag) => (
                    <SelectItem key={flag} value={flag}>
                      {flag}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>

            <p className="text-sm text-muted-foreground">
              Viewing entities under <strong>{selectedFeature}</strong>
            </p>
          </CardContent>
        </Card>

        {/* Entity and Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            {selectedFeature === "DRIVER" ? (
              <DriverList onSelectDriver={setSelectedEntityId} />
            ) : (
              <Card className="h-full flex items-center justify-center">
                <CardContent className="text-center text-muted-foreground">
                  Entity view not implemented for {selectedFeature}
                </CardContent>
              </Card>
            )}
          </div>

          <div className="lg:col-span-2">
            {selectedEntityId ? (
              <DriverAnalytics driverId={selectedEntityId} />
            ) : (
              <Card className="h-full flex items-center justify-center">
                <CardContent className="text-center py-12">
                  <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    Select an entity to view detailed analytics
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Simple reusable stat card
const OverviewCard = ({
  title,
  value,
  icon,
  subtitle,
}: {
  title: string;
  value: string | number;
  icon: JSX.Element;
  subtitle?: string;
}) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <div className="text-muted-foreground">{icon}</div>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
    </CardContent>
  </Card>
);

export default Admin;
