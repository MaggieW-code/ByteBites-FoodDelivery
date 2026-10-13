import type { RestaurantCardProps } from "../types/restaurantCard.ts"
/**
 * Generic card for spawning in restaurants and keeping
 * the app modular
 */ 

export function RestaurantCard({
  imageUrl,
  cuisineType,
  title,
  avgRating,
  qtyRating,
  description,
  maxWait,
  minWait,
  delPrice,
  minPayment
}: RestaurantCardProps) {
  return (
    <button className="restaurant-card_button">
        <div className="restaurant-card_image_group">
            <img className="restaurant-card_image" src={imageUrl} alt={title}></img>
            <div className="restaurant-card_type">{cuisineType}</div>
        </div>
        <div className="restaurant-card_description_box">
            <h3 className="restaurant-card_title">{title}</h3>
            <div className="restaurant-card_ratings">
                <span className="text-amber-400 text-sm">★</span>
                <span>{avgRating}</span>
                <span>({qtyRating})</span>
            </div>
            <p className="restaurant-card_description">{description}</p>
            <div className="restaurant-card_quick_info">
                <span className="restaurant-card_wait_times">
                     <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        fill="currentColor"
                        className="bi bi-clock"
                        viewBox="0 0 16 16"
                    >
                        <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71z"></path>
                        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0"></path>
                    </svg>
                    {minWait} - {maxWait} min
                </span>
                <span>·</span>
                <span className="restaurant-card_delivery_charge">${delPrice}</span>
                <span>·</span>
                <span className="restaurant-card_min_payment">${minPayment} min</span>
            </div>
        </div>
    </button>
  );
}