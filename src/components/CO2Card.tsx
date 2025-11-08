import { Card } from "@/components/ui/card";
import { CloudRain } from "lucide-react";

interface CO2CardProps {
  co2Saved?: number;
}

const CO2Card = ({ co2Saved = 12.4 }: CO2CardProps) => {
  return (
    <Card className="p-6 hover:shadow-lg transition-shadow animate-fade-in" style={{ animationDelay: "0.1s" }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">CO₂ Saved</h3>
        <CloudRain className="h-5 w-5 text-primary" />
      </div>
      
      <div className="space-y-2">
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold text-primary">{co2Saved}</span>
          <span className="text-lg text-muted-foreground">kg</span>
        </div>
        <p className="text-sm text-muted-foreground">This month</p>
        
        <div className="pt-4 flex items-center gap-2">
          <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full" style={{ width: "62%" }}></div>
          </div>
          <span className="text-xs text-muted-foreground">62%</span>
        </div>
      </div>
    </Card>
  );
};

export default CO2Card;
