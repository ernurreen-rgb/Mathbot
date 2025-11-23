// web/next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next.js-ке output (шығыс) папкасын (мысалы, .next) дұрыс өңдеуге көмектеседі
  output: 'standalone',

  // React Strict Mode әзірлеу кезіндегі қателерді табуға көмектеседі
  reactStrictMode: true,

  // Жобаңыздың түбіріне қатысты статикалық активтерге (мысалы, /public) дұрыс сілтеу үшін
  // Бұл /web/public папкасын дұрыс өңдеуге көмектесуі керек.
  basePath: '', 

  // Егер Vercel-де .next шығыс папкасы табылмай жатса, оны Next.js-ке анық айтамыз.
  // outDir: './.next',  // Бұл әдетте қажет емес, бірақ қатені шешуі мүмкін
};

module.exports = nextConfig;