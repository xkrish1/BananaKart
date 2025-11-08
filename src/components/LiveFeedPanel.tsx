import { Card } from "@/components/ui/card";
import { Clock } from "lucide-react";

interface FeedItem {
  id: number;
  recipe: string;
  time: string;
  score: number;
}

const LiveFeedPanel = () => {
  const feedItems: FeedItem[] = [
    { id: 1, recipe: "Pasta Carbonara", time: "2 min ago", score: 85 },
    { id: 2, recipe: "Greek Salad", time: "15 min ago", score: 92 },
    { id: 3, recipe: "Chicken Stir Fry", time: "1 hour ago", score: 78 },
    { id: 4, recipe: "Veggie Tacos", time: "2 hours ago", score: 88 },
  ];

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow animate-slide-up" style={{ animationDelay: "0.2s" }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">Recent Analyses</h3>
        <Clock className="h-5 w-5 text-primary" />
      </div>
      
      <div className="space-y-3">
        {feedItems.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg hover:bg-secondary/50 transition-colors"
          >
            <div className="flex-1">
              <p className="text-sm font-medium text-foreground">{item.recipe}</p>
              <p className="text-xs text-muted-foreground">{item.time}</p>
            </div>
            <div className="text-right">
              <span className="text-lg font-bold text-primary">{item.score}</span>
              <p className="text-xs text-muted-foreground">score</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default LiveFeedPanel;
