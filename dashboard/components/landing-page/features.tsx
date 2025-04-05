"use client"
import { motion } from "framer-motion"

export default function Features() {
  const fadeUpVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 1, delay: 0.5 + i * 0.2, ease: "easeInOut" }
    })
  }

  const features = [
    {
      title: "Real-Time Insights",
      description: "Get instant AI-driven analysis from your store and customer data.",
    },
    {
      title: "Slack Integration",
      description: "Query and receive insights directly in your Slack workspace.",
    },
    {
      title: "Data Automation",
      description: "Seamlessly connect PostgreSQL and marketplace platforms.",
    },
  ]

  return (
    <div id="features" className="w-full py-16 bg-gradient-to-br from-green-900 to-white/5 overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          custom={0}
          variants={fadeUpVariants}
          initial="hidden"
          animate="visible"
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
            Features
          </h1>
          <p className="text-base sm:text-lg md:text-xl text-white/60 max-w-2xl mx-auto font-light">
            Discover how Sync Mind transforms your commerce experience.
          </p>
        </motion.div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              custom={index + 1}
              variants={fadeUpVariants}
              initial="hidden"
              animate="visible"
              className="relative bg-green-800/10 backdrop-blur-md border border-green-200/20 rounded-xl p-6 shadow-lg"
            >
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-green-500/10 to-transparent" />
              <div className="relative z-10">
                <h3 className="text-xl md:text-2xl font-semibold text-green-300 mb-3">
                  {feature.title}
                </h3>
                <p className="text-base md:text-lg text-white/70 font-light">
                  {feature.description}
                </p>
              </div>
              <motion.div
                animate={{ y: [0, 8, 0] }}
                transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -top-3 -right-3 w-10 h-10 bg-green-400/20 rounded-full border border-white/10"
              />
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}