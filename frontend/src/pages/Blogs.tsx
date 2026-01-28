import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { ArrowRight, Clock, User, Tag } from "lucide-react";
import blogsBg from "@/assets/bg-blogs.jpg";

const featuredPost = {
  title: "Understanding the Connection Between Sleep and Mental Health",
  excerpt: "Sleep and mental health are deeply interconnected. Discover how improving your sleep habits can significantly impact your emotional well-being and cognitive function.",
  author: "Dr. Sarah Mitchell",
  date: "December 28, 2024",
  readTime: "8 min read",
  category: "Wellness",
};

const posts = [
  {
    title: "5 Mindfulness Techniques for Daily Stress Relief",
    excerpt: "Simple, practical mindfulness exercises you can incorporate into your daily routine to manage stress effectively.",
    author: "Dr. Emily Rodriguez",
    date: "December 22, 2024",
    readTime: "5 min read",
    category: "Mindfulness",
  },
  {
    title: "Navigating Anxiety in the Digital Age",
    excerpt: "How our constant connection to technology affects anxiety levels and strategies to create healthy digital boundaries.",
    author: "Dr. James Chen",
    date: "December 18, 2024",
    readTime: "7 min read",
    category: "Anxiety",
  },
  {
    title: "The Power of Vulnerability in Relationships",
    excerpt: "Why emotional vulnerability strengthens connections and how to practice it safely in your relationships.",
    author: "Dr. Sarah Mitchell",
    date: "December 12, 2024",
    readTime: "6 min read",
    category: "Relationships",
  },
  {
    title: "Building Resilience: Lessons from Cognitive Behavioral Therapy",
    excerpt: "Key CBT principles that can help you develop mental resilience and cope with life's challenges.",
    author: "Dr. Emily Rodriguez",
    date: "December 8, 2024",
    readTime: "9 min read",
    category: "Therapy",
  },
  {
    title: "Understanding Burnout: Signs, Causes, and Recovery",
    excerpt: "A comprehensive guide to recognizing burnout symptoms and evidence-based strategies for recovery.",
    author: "Michael Thompson",
    date: "December 2, 2024",
    readTime: "10 min read",
    category: "Wellness",
  },
  {
    title: "The Role of Community in Mental Health Recovery",
    excerpt: "How social connections and community support contribute to mental health healing and maintenance.",
    author: "Dr. James Chen",
    date: "November 28, 2024",
    readTime: "6 min read",
    category: "Community",
  },
];

const categories = ["All", "Wellness", "Mindfulness", "Anxiety", "Relationships", "Therapy", "Community"];

const Blogs = () => {
  const [activeCategory, setActiveCategory] = useState("All");

  const filteredPosts = activeCategory === "All" 
    ? posts 
    : posts.filter(post => post.category === activeCategory);

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${blogsBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background/95 via-background/80 to-background/70" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0s", animationFillMode: "forwards" }}>
              Mental Health Blog
            </h1>
            <p className="text-lg text-muted-foreground animate-fade-up opacity-0" style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}>
              Insights, tips, and resources from our team of mental health experts to support your wellness journey.
            </p>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-8 border-b border-border bg-card">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap justify-center gap-2">
            {categories.map((category, index) => (
              <button
                key={index}
                onClick={() => setActiveCategory(category)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                  activeCategory === category
                    ? "bg-primary text-primary-foreground shadow-soft"
                    : "bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Post */}
      <section className="py-16 md:py-20">
        <div className="container mx-auto px-4">
          <ScrollReveal>
            <div className="max-w-4xl mx-auto">
              <div className="p-8 md:p-12 rounded-2xl bg-card border border-border card-hover">
                <span className="inline-block px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
                  Featured
                </span>
                <h2 className="font-display text-2xl md:text-3xl font-semibold text-foreground mb-4">
                  {featuredPost.title}
                </h2>
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  {featuredPost.excerpt}
                </p>
                <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-6">
                  <span className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {featuredPost.author}
                  </span>
                  <span className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    {featuredPost.readTime}
                  </span>
                  <span className="flex items-center gap-2">
                    <Tag className="w-4 h-4" />
                    {featuredPost.category}
                  </span>
                </div>
                <Button variant="hero">
                  Read Article
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Blog Posts Grid */}
      <section className="py-16 md:py-20 bg-card border-y border-border">
        <div className="container mx-auto px-4">
          <ScrollReveal>
            <h2 className="font-display text-2xl md:text-3xl font-semibold text-foreground mb-8 text-center">
              Latest Articles
            </h2>
          </ScrollReveal>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPosts.map((post, index) => (
              <ScrollReveal key={index} delay={index * 80}>
                <article className="group p-6 rounded-2xl bg-background border border-border card-hover h-full">
                  <span className="inline-block px-3 py-1 rounded-full bg-accent text-accent-foreground text-xs font-medium mb-4">
                    {post.category}
                  </span>
                  <h3 className="font-display text-lg font-semibold text-foreground mb-3 group-hover:text-primary transition-colors duration-200">
                    {post.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                    {post.excerpt}
                  </p>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{post.author}</span>
                    <span>{post.readTime}</span>
                  </div>
                </article>
              </ScrollReveal>
            ))}
          </div>

          <ScrollReveal delay={500}>
            <div className="text-center mt-12">
              <Button variant="outline" size="lg">
                Load More Articles
                <ArrowRight className="w-5 h-5" />
              </Button>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Newsletter CTA */}
      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4 text-center">
          <ScrollReveal>
            <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
              Stay Updated
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
              Subscribe to our newsletter for the latest mental health insights, tips, and resources delivered to your inbox.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all duration-200"
              />
              <Button variant="hero">Subscribe</Button>
            </div>
          </ScrollReveal>
        </div>
      </section>
    </Layout>
  );
};

export default Blogs;