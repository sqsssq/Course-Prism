import Head from 'next/head';
import { useRouter } from 'next/router';

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string;
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  canonical?: string;
  structuredData?: object;
}

const SEOHead: React.FC<SEOHeadProps> = ({
  title = '港科大（广州）课程评价',
  description = '由学生维护的课程评价与选课参考平台。',
  keywords = 'HKUST(GZ),港科大广州,课程评价,选课参考',
  ogTitle,
  ogDescription,
  ogImage = '/favicon.ico',
  canonical,
  structuredData
}) => {
  const router = useRouter();
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL;
  const currentUrl = siteUrl ? `${siteUrl}${router.asPath}` : undefined;
  
  return (
    <Head>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      
      {/* Canonical URL */}
      {(canonical || currentUrl) && <link rel="canonical" href={canonical || currentUrl} />}
      
      {/* Open Graph / Facebook */}
      <meta property="og:type" content="website" />
      {currentUrl && <meta property="og:url" content={currentUrl} />}
      <meta property="og:title" content={ogTitle || title} />
      <meta property="og:description" content={ogDescription || description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:site_name" content="港科大（广州）课程评价" />
      
      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      {currentUrl && <meta property="twitter:url" content={currentUrl} />}
      <meta property="twitter:title" content={ogTitle || title} />
      <meta property="twitter:description" content={ogDescription || description} />
      <meta property="twitter:image" content={ogImage} />
      
      {/* Structured Data */}
      {structuredData && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(structuredData)
          }}
        />
      )}
    </Head>
  );
};

export default SEOHead;
