import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search } from "lucide-react";
import { cn } from "@/lib/utils";

interface Driver {
  id: string;
  name: string;
  score: number;
  feedbackCount: number;
  status: "excellent" | "good" | "attention";
}

interface DriverListProps {
  onSelectDriver: (driverId: string) => void;
}

const DriverList = ({ onSelectDriver }: DriverListProps) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Mock data - in production, fetch from API
  const drivers: Driver[] = [
    { id: "D001", name: "John Smith", score: 4.8, feedbackCount: 45, status: "excellent" },
    { id: "D002", name: "Sarah Johnson", score: 4.5, feedbackCount: 38, status: "excellent" },
    { id: "D003", name: "Mike Davis", score: 4.2, feedbackCount: 52, status: "good" },
    { id: "D004", name: "Emma Wilson", score: 3.8, feedbackCount: 29, status: "attention" },
    { id: "D005", name: "James Brown", score: 4.6, feedbackCount: 41, status: "excellent" },
    { id: "D006", name: "Lisa Anderson", score: 4.1, feedbackCount: 33, status: "good" },
    { id: "D007", name: "David Martinez", score: 3.9, feedbackCount: 27, status: "attention" },
    { id: "D008", name: "Amy Taylor", score: 4.7, feedbackCount: 48, status: "excellent" },
  ];

  const filteredDrivers = drivers.filter(
    (driver) =>
      driver.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      driver.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelectDriver = (driverId: string) => {
    setSelectedId(driverId);
    onSelectDriver(driverId);
  };

  const getStatusColor = (status: Driver["status"]) => {
    switch (status) {
      case "excellent":
        return "bg-success text-success-foreground";
      case "good":
        return "bg-primary text-primary-foreground";
      case "attention":
        return "bg-warning text-warning-foreground";
    }
  };

  const getStatusLabel = (status: Driver["status"]) => {
    switch (status) {
      case "excellent":
        return "Excellent";
      case "good":
        return "Good";
      case "attention":
        return "Needs Attention";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Drivers</CardTitle>
        <CardDescription>Select a driver to view analytics</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search drivers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
          {filteredDrivers.map((driver) => (
            <button
              key={driver.id}
              onClick={() => handleSelectDriver(driver.id)}
              className={cn(
                "w-full text-left p-4 rounded-lg border transition-all",
                selectedId === driver.id
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50 hover:bg-muted/50"
              )}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-semibold">{driver.name}</p>
                  <p className="text-sm text-muted-foreground">{driver.id}</p>
                </div>
                <Badge variant="secondary" className={getStatusColor(driver.status)}>
                  {getStatusLabel(driver.status)}
                </Badge>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">
                  Score: <span className="font-medium text-foreground">{driver.score}</span>
                </span>
                <span className="text-muted-foreground">
                  {driver.feedbackCount} feedback
                </span>
              </div>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default DriverList;
