import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { MessageSquare, LogOut } from "lucide-react";

type FeatureFlags = {
  driver: boolean;
  trip: boolean;
  mobile_app: boolean;
  marshal: boolean;
};

const Feedback = () => {
  const navigate = useNavigate();
  const [featureFlags, setFeatureFlags] = useState<FeatureFlags>({
    driver: true,
    trip: true,
    mobile_app: true,
    marshal: true,
  });
  const [entityType, setEntityType] = useState("");
  const [entityId, setEntityId] = useState("");
  const [feedbackText, setFeedbackText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/auth");
      return;
    }

    // Mock fetching feature flags from API
    // In production: fetch from /admin/config
    setFeatureFlags({
      driver: true,
      trip: true,
      mobile_app: true,
      marshal: true,
    });
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!entityType || !entityId || !feedbackText) {
      toast.error("Please fill in all fields");
      return;
    }

    setIsSubmitting(true);

    // Mock API call - in production, this would call your Flask API /feedback endpoint
    setTimeout(() => {
      toast.success("Feedback submitted successfully!");
      setEntityType("");
      setEntityId("");
      setFeedbackText("");
      setIsSubmitting(false);
    }, 1000);
  };

  const availableEntityTypes = Object.entries(featureFlags)
    .filter(([_, enabled]) => enabled)
    .map(([type]) => type);

  const getEntityLabel = (type: string) => {
    const labels: Record<string, string> = {
      driver: "Driver",
      trip: "Trip",
      mobile_app: "Mobile App",
      marshal: "Marshal",
    };
    return labels[type] || type;
  };

  const getEntityIdPlaceholder = (type: string) => {
    const placeholders: Record<string, string> = {
      driver: "Enter driver ID",
      trip: "Enter trip ID",
      mobile_app: "Enter app version or session ID",
      marshal: "Enter marshal ID",
    };
    return placeholders[type] || "Enter ID";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <nav className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold">Feedback System</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {localStorage.getItem("username")}
            </span>
            <Button variant="outline" size="sm" onClick={() => navigate("/admin")}>
              Admin Dashboard
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Submit Feedback</CardTitle>
              <CardDescription>
                Share your experience to help us improve our services
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="entity-type">Feedback Type</Label>
                  <Select value={entityType} onValueChange={setEntityType}>
                    <SelectTrigger id="entity-type">
                      <SelectValue placeholder="Select feedback type" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableEntityTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {getEntityLabel(type)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {entityType && (
                  <div className="space-y-2">
                    <Label htmlFor="entity-id">
                      {getEntityLabel(entityType)} ID
                    </Label>
                    <Input
                      id="entity-id"
                      value={entityId}
                      onChange={(e) => setEntityId(e.target.value)}
                      placeholder={getEntityIdPlaceholder(entityType)}
                      required
                    />
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="feedback-text">Your Feedback</Label>
                  <Textarea
                    id="feedback-text"
                    value={feedbackText}
                    onChange={(e) => setFeedbackText(e.target.value)}
                    placeholder="Share your experience in detail..."
                    rows={6}
                    required
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={isSubmitting || !entityType}
                >
                  {isSubmitting ? "Submitting..." : "Submit Feedback"}
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card className="mt-6 bg-muted/50">
            <CardContent className="pt-6">
              <h3 className="font-semibold mb-2">Available Feedback Types:</h3>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(featureFlags).map(([type, enabled]) => (
                  <div
                    key={type}
                    className={`flex items-center gap-2 text-sm ${
                      enabled ? "text-success" : "text-muted-foreground"
                    }`}
                  >
                    <div
                      className={`h-2 w-2 rounded-full ${
                        enabled ? "bg-success" : "bg-muted-foreground"
                      }`}
                    />
                    {getEntityLabel(type)}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Feedback;
