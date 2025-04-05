"use client"
import { motion } from "framer-motion"

export default function ProblemSolutionCards() {
  const fadeUpVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 1, delay: 0.5 + i * 0.2, ease: "easeInOut" }
    })
  }

  return (
    <div id="problem" className="w-full  flex items-center justify-center bg-gradient-to-br from-green-900 to-white/5 overflow-hidden">
      <div className="relative z-10 w-full container mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header and Description */}
        <motion.div
          custom={0}
          variants={fadeUpVariants}
          initial="hidden"
          animate="visible"
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
            Simplify Your Marketplace Success
          </h1>
          <p className="text-base sm:text-lg md:text-xl text-white/60 max-w-2xl mx-auto font-light">
            Overcome complexity with AI-powered tools designed for seamless commerce.
          </p>
        </motion.div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-5xl mx-auto">
          {/* Problem Card */}
          <motion.div
            custom={1}
            variants={fadeUpVariants}
            initial="hidden"
            animate="visible"
            className="relative bg-green-800/10 backdrop-blur-md border border-green-200/20 rounded-xl p-6 sm:p-8 shadow-lg"
          >
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-green-500/10 to-transparent" />
            <div className="relative z-10">
              <h2 className="text-2xl md:text-3xl font-medium text-white mb-4">
             Chaos
              </h2>
              <p className="text-base md:text-lg text-white/60 font-light">
                Selling on Amazon, eBay, Walmart, and your store is complex — scattered sales data and customer service overload demand more than listings.
              </p>
            </div>
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -top-4 -right-4 w-16 h-16 bg-green-400/20 rounded-full border border-white/10"
            />
          </motion.div>

          {/* Solution Card */}
          <motion.div
            custom={2}
            variants={fadeUpVariants}
            initial="hidden"
            animate="visible"
            className="relative bg-green-800/10 backdrop-blur-md border border-green-200/20 rounded-xl p-6 sm:p-8 shadow-lg"
          >
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-green-500/10 to-transparent" />
            <div className="relative z-10">
              <h2 className="text-2xl md:text-3xl font-medium text-green-300 mb-4">
               Harmony
              </h2>
              <p className="text-base md:text-lg text-white/70 font-light">
                Sync Mind, your AI-powered assistant, turns{" "}
                <span className="font-medium text-white">PostgreSQL</span>,{" "}
                <span className="font-medium text-white">store</span>, and{" "}
                <span className="font-medium text-white">customer service</span>{" "}
                data into actionable insights — delivered{" "}
                <span className="font-medium text-green-200">via Slack</span>.
              </p>
            </div>
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -bottom-4 -left-4 w-12 h-12 bg-green-400/20 rounded-full border border-white/10"
            />
          </motion.div>
        </div>
      </div>

      {/* Subtle Background Animation */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{ opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      >
        <div className="absolute inset-0 bg-gradient-to-t from-green-900/50 via-transparent to-green-900/50" />
      </motion.div>
    </div>
  )
}