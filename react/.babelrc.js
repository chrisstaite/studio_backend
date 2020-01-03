module.exports = {
  presets: [
    [
      "@babel/preset-react",
      {
        development: process.env.DEV === "true",
      },
    ],
  ],
};
