import React from 'react';
import { Navbar } from '@/components/layout/Navbar';
import { useUser } from '@/contexts/UserContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Calendar, CreditCard, Heart, BookOpen, Loader2 } from 'lucide-react';
import SEO from '@/components/SEO';

const UserDashboard = () => {
  const { user } = useUser();
  const [stats, setStats] = React.useState<any>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    // TODO: Fetch dashboard data from API
    // For now, using placeholder data
    setTimeout(() => {
      setStats({
        total_sessions: 0,
        upcoming_sessions: 0,
        total_events: 0,
        total_payments: 0,
        total_spent: 0,
        saved_blogs: 0,
        liked_blogs: 0
      });
      setIsLoading(false);
    }, 500);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 pt-32 pb-20">
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={`Dashboard - ${user?.name} - A-Cube`}
        description="Manage your sessions, events, payments, and saved content on A-Cube Mental Health Platform."
      />
      <div className="min-h-screen bg-background">
        <Navbar />
        
        <div className="container mx-auto px-4 pt-32 pb-20">
          {/* Welcome Header */}
          <div className="mb-8 animate-fade-in">
            <h1 className="text-3xl md:text-4xl font-display font-bold mb-2">
              Welcome back, {user?.name}! 👋
            </h1>
            <p className="text-muted-foreground">
              Here's an overview of your mental wellness journey
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="animate-slide-in-up" style={{ animationDelay: '0.1s' }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_sessions || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.upcoming_sessions || 0} upcoming
                </p>
              </CardContent>
            </Card>

            <Card className="animate-slide-in-up" style={{ animationDelay: '0.2s' }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Events Attended</CardTitle>
                <Heart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_events || 0}</div>
                <p className="text-xs text-muted-foreground">Total registrations</p>
              </CardContent>
            </Card>

            <Card className="animate-slide-in-up" style={{ animationDelay: '0.3s' }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Saved Content</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.saved_blogs || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.liked_blogs || 0} liked articles
                </p>
              </CardContent>
            </Card>

            <Card className="animate-slide-in-up" style={{ animationDelay: '0.4s' }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">₹{stats?.total_spent || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.total_payments || 0} transactions
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Tabs for different sections */}
          <Card className="animate-slide-in-up" style={{ animationDelay: '0.5s' }}>
            <CardHeader>
              <CardTitle>Your Activity</CardTitle>
              <CardDescription>
                View and manage your sessions, events, payments, and saved content
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="sessions" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="sessions">Sessions</TabsTrigger>
                  <TabsTrigger value="events">Events</TabsTrigger>
                  <TabsTrigger value="payments">Payments</TabsTrigger>
                  <TabsTrigger value="saved">Saved</TabsTrigger>
                </TabsList>
                
                <TabsContent value="sessions" className="space-y-4 mt-4">
                  <div className="text-center py-12 text-muted-foreground">
                    <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No sessions booked yet</p>
                    <p className="text-sm mt-2">Book your first therapy session to get started</p>
                  </div>
                </TabsContent>
                
                <TabsContent value="events" className="space-y-4 mt-4">
                  <div className="text-center py-12 text-muted-foreground">
                    <Heart className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No events registered yet</p>
                    <p className="text-sm mt-2">Check out our upcoming events and workshops</p>
                  </div>
                </TabsContent>
                
                <TabsContent value="payments" className="space-y-4 mt-4">
                  <div className="text-center py-12 text-muted-foreground">
                    <CreditCard className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No payment history yet</p>
                    <p className="text-sm mt-2">Your transactions will appear here</p>
                  </div>
                </TabsContent>
                
                <TabsContent value="saved" className="space-y-4 mt-4">
                  <div className="text-center py-12 text-muted-foreground">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No saved articles yet</p>
                    <p className="text-sm mt-2">Save articles from our blog to read later</p>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
};

export default UserDashboard;