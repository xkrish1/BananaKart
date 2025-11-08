import { Card } from "@/components/ui/card";
import { CloudRain, Car } from "lucide-react";

const WeatherTrafficCard = () => {
  return (
    <Card className="p-6 hover:shadow-lg transition-shadow animate-fade-in" style={{ animationDelay: "0.3s" }}>
      <h3 className="text-lg font-semibold text-foreground mb-4">Live Conditions</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
          <div className="flex items-center gap-3">
            <Car className="h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-foreground">Traffic</p>
              <p className="text-xs text-muted-foreground">Multiplier</p>
            </div>
          </div>
          <span className="text-2xl font-bold text-primary">1.2x</span>
        </div>
        
        <div className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
          <div className="flex items-center gap-3">
            <CloudRain className="h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-foreground">Weather</p>
              <p className="text-xs text-muted-foreground">Impact</p>
            </div>
          </div>
          <span className="text-2xl font-bold text-warning">0.9x</span>
        </div>
      </div>
    </Card>
  );
};

export default WeatherTrafficCard;
