export const mockCatalog = {
  stores: [
    {
      id: "1",
      name: "Green Valley Farm",
      products: [
        { id: "p1", name: "Organic Tomatoes", price: 4.99, category: "Vegetables", stock: 25 },
        { id: "p2", name: "Fresh Basil", price: 3.49, category: "Herbs", stock: 30 },
        { id: "p3", name: "Heirloom Lettuce", price: 5.99, category: "Vegetables", stock: 15 },
      ],
    },
  ],
  products: [
    { id: "p1", name: "Organic Tomatoes", price: 4.99, category: "Vegetables", image: "/ripe-tomato.png" },
    { id: "p2", name: "Fresh Basil", price: 3.49, category: "Herbs", image: "/fresh-basil.png" },
    { id: "p3", name: "Heirloom Lettuce", price: 5.99, category: "Vegetables", image: "/fresh-lettuce.png" },
    { id: "p4", name: "Local Honey", price: 12.99, category: "Specialty", image: "/golden-honey.png" },
    { id: "p5", name: "Farmer Cheese", price: 9.99, category: "Dairy", image: "/assorted-cheese-platter.png" },
  ],
}

export const mockKPI = {
  totalOrders: 234,
  activeSustainability: 1285,
  carbonReduction: "2.4T",
  communitySupported: 45,
}

export const mockOrders = [
  {
    id: "ORD-001",
    date: "2024-11-06",
    total: 34.99,
    status: "delivered",
    items: [
      { id: "p1", name: "Organic Tomatoes", quantity: 2, price: 4.99 },
      { id: "p2", name: "Fresh Basil", quantity: 1, price: 3.49 },
    ],
  },
]

export const mockRoutes = {
  clusters: [
    { id: "c1", lat: 40.7128, lng: -74.006, count: 12 },
    { id: "c2", lat: 40.758, lng: -73.9855, count: 8 },
    { id: "c3", lat: 40.7282, lng: -73.7949, count: 5 },
  ],
}
