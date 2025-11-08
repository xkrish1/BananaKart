import Navbar from "@/components/Navbar";
import EcoScoreCard from "@/components/EcoScoreCard";
import CO2Card from "@/components/CO2Card";
import VarianceCard from "@/components/VarianceCard";
import WeatherTrafficCard from "@/components/WeatherTrafficCard";
import ChartPlaceholder from "@/components/ChartPlaceholder";
import MapPlaceholder from "@/components/MapPlaceholder";
import LiveFeedPanel from "@/components/LiveFeedPanel";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Header */}
          <div className="animate-fade-in">
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-muted-foreground mt-2">
              Track your sustainability metrics and optimize your grocery shopping.
            </p>
          </div>
          
          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <EcoScoreCard />
            <CO2Card />
            <VarianceCard />
            <WeatherTrafficCard />
          </div>
          
          {/* Charts and Map Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartPlaceholder />
            <MapPlaceholder />
          </div>
          
          {/* Live Feed */}
          <LiveFeedPanel />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
