import { Head, Html, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="zh-CN">
      <Head>
        <link rel="shortcut icon" href="/favicon.ico" />
        <meta
          name="description"
          content="港科大（广州）课程评价与选课参考"
        ></meta>
        <meta
          name="keywords"
          content="HKUST(GZ),港科大广州,课程评价,选课参考"
        ></meta>
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
