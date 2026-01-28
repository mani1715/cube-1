import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Calendar, Users, BookOpen, MessageCircle, Gamepad2, PenTool, ArrowRight, DollarSign, Gift } from "lucide-react";
import eventsBg from "@/assets/bg-events.jpg";

const eventTypes = [
  {
    id: "panel",
    icon: Users,
    title: "Panel Discussions",
    description: "Engage with expert psychologists discussing critical mental health topics.",
    type: "Paid",
    price: "From $25",
    schedule: "Monthly",
    features: ["Live Q&A sessions", "Expert panel of 3-5 psychologists", "Recorded for later viewing", "Certificate of attendance"],
  },
  {
    id: "meetups",
    icon: Calendar,
    title: "Psychologist Meetups",
    description: "Networking events for mental health professionals to connect and collaborate.",
    type: "Paid",
    price: "From $15",
    schedule: "Bi-monthly",
    features: ["Professional networking", "Case study discussions", "Peer supervision opportunities", "Industry updates"],
  },
  {
    id: "seminars",
    icon: BookOpen,
    title: "Seminars & Workshops",
    description: "In-depth educational sessions on specific mental health topics and techniques.",
    type: "Paid",
    price: "From $50",
    schedule: "Weekly",
    features: ["Interactive learning", "Practical exercises", "Take-home materials", "Small group format"],
  },
  {
    id: "circles",
    icon: MessageCircle,
    title: "Open Circle Conversations",
    description: "Free, community-led discussions in a safe and supportive environment.",
    type: "Free",
    price: "Free",
    schedule: "Weekly",
    features: ["Open to everyone", "Peer support format", "Various topics", "No registration needed"],
  },
  {
    id: "writing",
    icon: PenTool,
    title: "Book Writing Collaborations",
    description: "Join our collaborative book writing projects sharing mental health insights.",
    type: "Free",
    price: "Free",
    schedule: "Ongoing",
    features: ["Collaborative authorship", "Publishing opportunities", "Writer community", "Expert guidance"],
  },
  {
    id: "gaming",
    icon: Gamepad2,
    title: "Gaming Night - Online",
    description: "Virtual gaming sessions to build community and reduce stress together.",
    type: "Free",
    price: "Free",
    schedule: "Weekly",
    features: ["Casual gaming environment", "Community building", "Stress relief", "All skill levels welcome"],
  },
];

const upcomingEvents = [
  {
    title: "Understanding Anxiety: Expert Panel",
    date: "January 15, 2025",
    time: "7:00 PM EST",
    type: "Panel Discussion",
    price: "$25",
  },
  {
    title: "Mindfulness Workshop for Beginners",
    date: "January 18, 2025",
    time: "10:00 AM EST",
    type: "Workshop",
    price: "$50",
  },
  {
    title: "Open Circle: New Year, New Mindset",
    date: "January 20, 2025",
    time: "6:00 PM EST",
    type: "Open Circle",
    price: "Free",
  },
  {
    title: "Gaming Night: Community Connect",
    date: "January 22, 2025",
    time: "8:00 PM EST",
    type: "Gaming Night",
    price: "Free",
  },
];

const faqs = [
  {
    question: "How do I register for an event?",
    answer: "You can register for any event through our events page. Simply click on the event you're interested in and follow the registration process. For paid events, you'll be directed to our secure payment portal.",
  },
  {
    question: "Are the events available online?",
    answer: "Yes! Most of our events are available both in-person and online. Virtual attendees receive the same interactive experience with live Q&A capabilities and access to recordings.",
  },
  {
    question: "What's your refund policy for paid events?",
    answer: "We offer full refunds up to 48 hours before the event start time. After that, you can transfer your ticket to a future event of equal or lesser value.",
  },
  {
    question: "Do I need any special equipment for virtual events?",
    answer: "Just a stable internet connection and a device with a camera and microphone. We use Zoom for most virtual events, which you can access through your browser or the app.",
  },
  {
    question: "Can I get a certificate for attending workshops?",
    answer: "Yes, we provide certificates of attendance for all paid workshops and seminars. These can be used for continuing education credits where applicable.",
  },
  {
    question: "Are the Open Circle Conversations confidential?",
    answer: "Absolutely. What's shared in Open Circles stays there. We maintain strict confidentiality guidelines, and all participants agree to respect each other's privacy.",
  },
];

const Events = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${eventsBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-background/60" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0s", animationFillMode: "forwards" }}>
              Events & Programs
            </h1>
            <p className="text-lg text-muted-foreground animate-fade-up opacity-0" style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}>
              Join our community through educational events, workshops, and supportive gatherings designed to promote mental wellness.
            </p>
          </div>
        </div>
      </section>

      {/* Event Types */}
      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
                Types of Events
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                We offer a diverse range of events to suit different interests and needs.
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {eventTypes.map((event, index) => (
              <ScrollReveal key={event.id} delay={index * 80}>
                <div className="p-6 rounded-2xl bg-card border border-border card-hover h-full">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-accent flex items-center justify-center">
                      <event.icon className="w-5 h-5 text-primary" />
                    </div>
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      event.type === "Free" 
                        ? "bg-green-100 text-green-700" 
                        : "bg-accent text-accent-foreground"
                    }`}>
                      {event.type === "Free" ? <Gift className="w-3 h-3" /> : <DollarSign className="w-3 h-3" />}
                      {event.price}
                    </span>
                  </div>
                  
                  <h3 className="font-display text-xl font-semibold text-foreground mb-2">
                    {event.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {event.description}
                  </p>
                  
                  <div className="text-xs text-primary font-medium mb-4">
                    Schedule: {event.schedule}
                  </div>
                  
                  <ul className="space-y-2">
                    {event.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-sm text-muted-foreground">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Upcoming Events */}
      <section className="py-20 md:py-28 bg-card border-y border-border">
        <div className="container mx-auto px-4">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
                Upcoming Events
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Don't miss out on our upcoming programs. Register today to secure your spot.
              </p>
            </div>
          </ScrollReveal>

          <div className="max-w-3xl mx-auto space-y-4">
            {upcomingEvents.map((event, index) => (
              <ScrollReveal key={index} delay={index * 80}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-background border border-border card-hover">
                  <div>
                    <h3 className="font-semibold text-foreground mb-1">{event.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {event.date} • {event.time}
                    </p>
                    <span className="inline-block mt-2 text-xs text-primary font-medium">
                      {event.type}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`font-semibold ${event.price === "Free" ? "text-green-600" : "text-foreground"}`}>
                      {event.price}
                    </span>
                    <Button variant="outline" size="sm">
                      Register
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* FAQs */}
      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <ScrollReveal>
              <div className="text-center mb-12">
                <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
                  Frequently Asked Questions
                </h2>
                <p className="text-muted-foreground">
                  Find answers to common questions about our events and programs.
                </p>
              </div>
            </ScrollReveal>

            <ScrollReveal delay={100}>
              <Accordion type="single" collapsible className="space-y-4">
                {faqs.map((faq, index) => (
                  <AccordionItem
                    key={index}
                    value={`faq-${index}`}
                    className="border border-border rounded-xl px-6 data-[state=open]:bg-card transition-colors duration-200"
                  >
                    <AccordionTrigger className="text-left font-semibold text-foreground hover:no-underline py-5">
                      {faq.question}
                    </AccordionTrigger>
                    <AccordionContent className="text-muted-foreground pb-5">
                      {faq.answer}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </ScrollReveal>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Events;