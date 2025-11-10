import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { TrendingUp, MessageSquare, Star } from "lucide-react";

interface DriverAnalyticsProps {
  driverId: string;
}

const DriverAnalytics = ({ driverId }: DriverAnalyticsProps) => {
  // Mock data - in production, fetch from /admin/driver/<driver_id> endpoint
  const driverData = {
    id: driverId,
    name: "John Smith",
    currentScore: 4.8,
    feedbackCount: 45,
    status: "excellent",
  };

  const scoreHistory = [
    { date: "Week 1", score: 4.2 },
    { date: "Week 2", score: 4.4 },
    { date: "Week 3", score: 4.6 },
    { date: "Week 4", score: 4.5 },
    { date: "Week 5", score: 4.7 },
    { date: "Week 6", score: 4.8 },
  ];

  const feedbackDistribution = [
    { category: "Excellent (5)", count: 28 },
    { category: "Good (4)", count: 12 },
    { category: "Average (3)", count: 4 },
    { category: "Poor (2)", count: 1 },
    { category: "Bad (1)", count: 0 },
  ];

  const recentFeedback = [
    {
      id: "F001",
      text: "Very professional and courteous driver. Smooth ride experience.",
      score: 5,
      timestamp: "2024-01-15T10:30:00",
    },
    {
      id: "F002",
      text: "Good service, arrived on time.",
      score: 4,
      timestamp: "2024-01-14T15:45:00",
    },
    {
      id: "F003",
      text: "Excellent driver, very safe and friendly.",
      score: 5,
      timestamp: "2024-01-13T09:20:00",
    },
  ];

  const getSentimentColor = (score: number) => {
    if (score >= 4.5) return "text-success";
    if (score >= 3.5) return "text-primary";
    return "text-warning";
  };

  return (
    <div className="space-y-6">
      {/* Driver Overview */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle>{driverData.name}</CardTitle>
              <CardDescription>Driver ID: {driverData.id}</CardDescription>
            </div>
            <Badge className="bg-success text-success-foreground">
              Excellent Performance
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <Star className="h-6 w-6 mx-auto mb-2 text-primary" />
              <p className="text-2xl font-bold">{driverData.currentScore}</p>
              <p className="text-sm text-muted-foreground">Current Score</p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <MessageSquare className="h-6 w-6 mx-auto mb-2 text-primary" />
              <p className="text-2xl font-bold">{driverData.feedbackCount}</p>
              <p className="text-sm text-muted-foreground">Total Feedback</p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <TrendingUp className="h-6 w-6 mx-auto mb-2 text-success" />
              <p className="text-2xl font-bold">+0.6</p>
              <p className="text-sm text-muted-foreground">Last 6 Weeks</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Score Trend */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Trend</CardTitle>
          <CardDescription>Average sentiment score over time</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={scoreHistory}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis domain={[0, 5]} className="text-xs" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={{ fill: "hsl(var(--primary))", r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Feedback Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Feedback Distribution</CardTitle>
          <CardDescription>Breakdown of ratings received</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={feedbackDistribution}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="category" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Recent Feedback */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Feedback</CardTitle>
          <CardDescription>Latest comments from riders</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentFeedback.map((feedback) => (
              <div
                key={feedback.id}
                className="p-4 border rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className={`font-semibold ${getSentimentColor(feedback.score)}`}>
                    Score: {feedback.score}/5
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(feedback.timestamp).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm">{feedback.text}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DriverAnalytics;
