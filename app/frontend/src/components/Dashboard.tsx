import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, Tooltip
} from "recharts";
import { DetailsList, IColumn } from "@fluentui/react";

export function Dashboard() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch("/view_stats")
      .then(res => res.json())
      .then(s => setStats(s));
  }, []);

  if (!stats) return <div>Loading…</div>;

  // prepare the table items
  const userItems = Object.entries(stats.viewsByUser).map(([username, count]) => ({
    username, count
  }));
  const columns: IColumn[] = [
    { key: "u", name: "User",    fieldName: "username", minWidth: 150 },
    { key: "v", name: "Views",   fieldName: "count",    minWidth: 50 }
  ];

  return (
    <div style={{ padding: 20 }}>
      {/* Top‐line cards */}
      <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
        <div style={{ flex: 1, padding: 10, border: "1px solid #ccc" }}>
          <h4>Total views</h4>
          <strong style={{ fontSize: 24 }}>{stats.totalViews}</strong>
        </div>
        <div style={{ flex: 1, padding: 10, border: "1px solid #ccc" }}>
          <h4>Total viewers</h4>
          <strong style={{ fontSize: 24 }}>{stats.totalViewers}</strong>
        </div>
      </div>

      {/* Two bar‐charts */}
      <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
        <div style={{ flex: 1, height: 200 }}>
          <h5>Views per day</h5>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.dailyViews}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" name="Views" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ flex: 1, height: 200 }}>
          <h5>Unique viewers per day</h5>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.dailyUniqueViewers}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" name="Unique Viewers" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Table of views by user */}
      <div>
        <h5>Views by user</h5>
        <DetailsList
          items={userItems}
          columns={columns}
          isHeaderVisible={true}
        />
      </div>
    </div>
  );
}
