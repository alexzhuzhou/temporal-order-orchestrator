@echo off
REM Register custom search attributes with Temporal using tctl
REM This script uses the tctl command-line tool inside the Temporal container

echo ==================================================
echo Setting up Temporal Search Attributes
echo ==================================================
echo.

echo Adding CustomerId (Keyword)...
docker exec temporal tctl admin cluster add-search-attributes --name CustomerId --type Keyword

echo Adding CustomerName (Text)...
docker exec temporal tctl admin cluster add-search-attributes --name CustomerName --type Text

echo Adding OrderTotal (Double)...
docker exec temporal tctl admin cluster add-search-attributes --name OrderTotal --type Double

echo Adding Priority (Keyword)...
docker exec temporal tctl admin cluster add-search-attributes --name Priority --type Keyword

echo.
echo Search attributes setup complete!
echo.
echo Registered attributes:
echo   - CustomerId (Keyword): Query by exact customer ID
echo   - CustomerName (Text): Search by customer name
echo   - OrderTotal (Double): Filter by order amount
echo   - Priority (Keyword): Filter by priority level
echo.
pause
