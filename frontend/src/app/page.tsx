import DashboardPage from './(dashboard)/page';
import DashboardLayout from './(dashboard)/layout';

export default function RootPage() {
  return (
    <DashboardLayout>
      <DashboardPage />
    </DashboardLayout>
  );
}
