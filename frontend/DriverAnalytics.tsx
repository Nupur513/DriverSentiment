// src/components/admin/DriverAnalytics.tsx
import { useEffect, useState } from "react";
import api from "./src/api/axiosInstance";
import { Card, CardHeader, CardTitle, CardContent } from "./src/components/ui/card";

interface Props {
  driverId: string;
}

const DriverAnalytics = ({ driverId }: Props) => {
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      const res = await api.get(`/driver/${driverId}`);
      setAnalytics(res.data.analytics);
    };
    fetchAnalytics();
  }, [driverId]);

  if (!analytics) return <div>Loading analytics...</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Driver Analytics: {analytics.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Score: {analytics.current_score ?? "N/A"}</p>
        <p>Feedback Count: {analytics.feedback_count}</p>
      </CardContent>
    </Card>
  );
};

export default DriverAnalytics;
