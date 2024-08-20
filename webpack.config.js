const path = require("path");
const webpack = require("webpack");

const BundleTracker = require("webpack-bundle-tracker");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { VueLoaderPlugin } = require("vue-loader");

const devEnv = process.env.NODE_ENV !== "production";
const hotReload = process.env.HOT_RELOAD === "1";

const statsFile = devEnv ? "webpack-stats-dev.json" : "webpack-stats.json";

const plugins = [
  new BundleTracker({ filename: statsFile }),
  new VueLoaderPlugin(),
  new MiniCssExtractPlugin({
    filename: devEnv ? "[name].css" : "[name].[fullhash].css",
    chunkFilename: devEnv ? "[id].css" : "[id].[fullhash].css",
  }),
  new CleanWebpackPlugin(),
];

const styleRule = {
  test: /\.(sa|sc|c)ss$/,
  use: [
    MiniCssExtractPlugin.loader,
    { loader: "css-loader", options: { sourceMap: true } },
    "postcss-loader",
    "sass-loader",
  ],
};

if (devEnv) {
  styleRule.use = ["css-hot-loader", ...styleRule.use];
} else {
  plugins.push(new webpack.EnvironmentPlugin(["NODE_ENV", "SOURCE_VERSION"]));
}

module.exports = {
  context: __dirname,
  entry: {
    app: "./frontend/app/js/app/app.js",
  },
  output: {
    path: path.resolve("./static/dist/"),
    filename: "[name]-[fullhash].js",
    publicPath: hotReload ? "/webpack-dist/" : "",
  },
  devtool: devEnv ? "eval-cheap-source-map" : "source-map",
  devServer: {
    hot: true,
    headers: { "Access-Control-Allow-Origin": "*" },
    allowedHosts: ["gobabygo-webpack-1", "localhost"],
    client: {
      webSocketURL: "auto://localhost:8888/webpack-ws",
    },
  },
  resolve: {
    alias: {
      "@frontend": path.resolve(__dirname, "frontend/"),
      "@app": path.resolve(__dirname, "frontend/app/js/app/"),
    },
    fallback: { url: require.resolve("url/") },
  },
  module: {
    rules: [
      styleRule,
      {
        test: /\.vue$/,
        use: "vue-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.js$/,
        loader: "babel-loader",
        include: path.resolve("./frontend/app/js"),
        exclude: /node_modules/,
      },
      {
        test: /.(jpg|png|woff(2)?|eot|ttf|svg)$/,
        loader: "file-loader",
      },
    ],
  },
  plugins,
};
