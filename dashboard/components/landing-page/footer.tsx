"use client"
import { motion } from "framer-motion"

export default function Footer() {
  const fadeUpVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 1, ease: "easeInOut" }
    }
  }

  return (
    <footer className="w-full bg-green-900/80 py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={fadeUpVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col md:flex-row justify-between items-center gap-6"
        >
          {/* Brand */}
          <div className="text-center md:text-left">
            <h3 className="text-2xl font-bold text-white">Sync Mind</h3>
            <p className="text-sm text-green-200/70 mt-1">
              AI Agent powered commerce, simplified.
            </p>
          </div>

          {/* Links */}
          <div className="flex flex-col sm:flex-row gap-6 text-center">
            <a href="#features" className="text-green-200 hover:text-white transition-colors duration-300">
              Features
            </a>
            <a href="#problem" className="text-green-200 hover:text-white transition-colors duration-300">
              Challenges
            </a>
            <a href="#" className="text-green-200 hover:text-white transition-colors duration-300">
              Contact
            </a>
          </div>

          {/* Copyright */}
          <p className="text-sm text-white/60">
            © {new Date().getFullYear()} Sync Mind. All rights reserved.
          </p>
        </motion.div>
      </div>

      {/* Subtle Animation */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{ opacity: [0.2, 0.4, 0.2] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      >
        <div className="absolute inset-0 bg-gradient-to-t from-green-800/20 to-transparent" />
      </motion.div>
    </footer>
  )
}