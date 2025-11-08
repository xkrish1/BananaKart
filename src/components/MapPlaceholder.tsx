import { Card } from "@/components/ui/card";
import { MapPin } from "lucide-react";

const MapPlaceholder = () => {
  return (
    <Card className="p-6 hover:shadow-lg transition-shadow animate-slide-up" style={{ animationDelay: "0.1s" }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">Route & Suppliers</h3>
        <MapPin className="h-5 w-5 text-primary" />
      </div>
      
      <div className="relative h-64 bg-secondary rounded-lg overflow-hidden">
        {/* Simplified map illustration */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-primary/10" />
        
        {/* Mock route line */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path
            d="M 20,80 Q 50,20 80,40"
            fill="none"
            stroke="hsl(var(--primary))"
            strokeWidth="0.5"
            strokeDasharray="2,2"
          />
        </svg>
        
        {/* Mock location pins */}
        <div className="absolute top-[20%] left-[20%] w-4 h-4 bg-primary rounded-full border-2 border-card shadow-lg animate-pulse" />
        <div className="absolute top-[40%] left-[50%] w-4 h-4 bg-warning rounded-full border-2 border-card shadow-lg animate-pulse" style={{ animationDelay: "0.2s" }} />
        <div className="absolute top-[60%] left-[80%] w-4 h-4 bg-primary rounded-full border-2 border-card shadow-lg animate-pulse" style={{ animationDelay: "0.4s" }} />
        
        {/* Center text overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center bg-card/90 backdrop-blur-sm px-4 py-2 rounded-lg border border-border">
            <p className="text-xs text-muted-foreground">Map visualization</p>
            <p className="text-sm font-medium text-foreground">3 suppliers nearby</p>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default MapPlaceholder;
