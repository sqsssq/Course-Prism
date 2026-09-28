import { Button, Card, Spin, message } from "antd";
import Head from "next/head";
import { useRouter } from "next/router";
import { useEffect } from "react";

import PageHeader from "@/components/page-header";
import ReviewList from "@/components/review-list";
import Config from "@/config/config";
import { Pagination } from "@/lib/models";
import { useFollowedReviews } from "@/services/review";
import { useUser } from "@/services/user";

const FollowReviewPage = () => {
  const { user, loading: userLoading, error } = useUser();
  const router = useRouter();
  const { page, size } = router.query;

  const pagination: Pagination = {
    page: page ? parseInt(page as string) : 1,
    pageSize: size ? parseInt(size as string) : Config.PAGE_SIZE,
  };

  // 立即检查登录状态并重定向
  useEffect(() => {
    if (!userLoading && !user) {
      message.warning("请先登录后查看关注的点评");
      router.replace("/login?next=/follow-review");
      return;
    }
  }, [user, userLoading, router]);

  // 只有在用户已登录时才调用数据接口
  const shouldFetchData = !userLoading && !!user;
  const { reviews, loading } = useFollowedReviews(shouldFetchData ? pagination : null);

  // 如果未登录或正在加载，立即重定向，不显示任何内容
  if (userLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  // 如果未登录，立即返回null，避免闪烁
  if (!user) {
    return null;
  }

  const onPageChange = (page: number, pageSize: number) => {
    router.push({ query: { page: page, size: pageSize } });
  };

  return (
    <>
      <PageHeader
        title="关注课程的点评"
        subTitle={`共有${reviews ? reviews.count : 0}个点评`}
        extra={
          <Button
            type="link"
            onClick={() => {
              router.push("/follow-course");
            }}
          >
            关注的课程
          </Button>
        }
      ></PageHeader>
      <Head>
        <title>关注 - 港科大（广州）课程评价</title>
      </Head>
      <Card>
        <ReviewList
          loading={loading}
          count={reviews?.count}
          reviews={reviews?.results}
          onPageChange={onPageChange}
          pagination={pagination}
        />
      </Card>
    </>
  );
};

export default FollowReviewPage;
